##############################################################################
#
# Copyright (c) 2002-2026 Nexedi SA and Contributors. All Rights Reserved.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
##############################################################################
"""Format independent part of ``Manager.granulateFile``.

Format specific granulators (``handler.ooo.granulator.OOGranulator``,
``handler.pdf.granulator.PdfGranulator``) extract a flat list of *blocks* in
reading order::

  {"type": "heading" | "paragraph" | "list_item" | "footnote" | "table",
   "text": "...",
   "level": 2,        # headings only
   "page": 4}         # only when the format has pages

This module annotates these blocks with their position in the section tree and
packs them into *grains* (chunks) suitable for embedding and retrieval.
"""

import re
from hashlib import sha256

STRATEGY_LIST = ('structure', 'page', 'fixed', 'blocks')
DEFAULT_MAX_CHARS = 1500
DEFAULT_OVERLAP_CHARS = 200
BLOCK_SEPARATOR = '\n\n'
CONTEXT_SEPARATOR = ' > '
TABLE_CELL_SEPARATOR = ' | '

_SENTENCE_END = '.!?\u3002\uff01\uff1f'
_SENTENCE_BOUNDARY_RE = re.compile(r'(?<=[%s])\s+' % _SENTENCE_END)
_WHITESPACE_RE = re.compile(r'\s+')


class GranulateError(ValueError):
  """Raised when a document can not be granulated (bad options, corrupt or
  encrypted document, extraction failure, ...)."""


def parseGranulateKw(granulate_kw):
  """Validate user supplied options and return them with defaults applied."""
  granulate_kw = dict(granulate_kw or {})
  options = {
    'strategy': granulate_kw.pop('strategy', 'structure'),
    'max_chars': granulate_kw.pop('max_chars', DEFAULT_MAX_CHARS),
    'overlap_chars': granulate_kw.pop('overlap_chars', DEFAULT_OVERLAP_CHARS),
    'include_tables': granulate_kw.pop('include_tables', True),
    'page_range': granulate_kw.pop('page_range', None),
  }
  if granulate_kw:
    raise GranulateError(
      'Unknown granulate option(s): %s' % ', '.join(sorted(granulate_kw)))
  if options['strategy'] not in STRATEGY_LIST:
    raise GranulateError('strategy must be one of %s' % ', '.join(STRATEGY_LIST))
  for name in ('max_chars', 'overlap_chars'):
    value = options[name]
    if isinstance(value, bool) or not isinstance(value, int):
      raise GranulateError('%s must be an integer' % name)
  if options['max_chars'] < 100:
    raise GranulateError('max_chars must be at least 100')
  if not 0 <= options['overlap_chars'] <= options['max_chars'] // 2:
    raise GranulateError('overlap_chars must be between 0 and max_chars / 2')
  page_range = options['page_range']
  if page_range is not None:
    try:
      first, last = page_range
      first, last = int(first), int(last)
    except (TypeError, ValueError):
      raise GranulateError('page_range must be [first_page, last_page]')
    if first < 1 or last < first:
      raise GranulateError('page_range must satisfy 1 <= first <= last')
    options['page_range'] = (first, last)
  options['include_tables'] = bool(options['include_tables'])
  return options


def annotateBlockList(block_list, initial_heading_list=()):
  """Set ``id`` and ``section_path`` on each block (in place).

  ``initial_heading_list`` is a list of ``(level, title)`` that are already
  open when the first block starts, which lets a document be processed by
  page ranges without losing the enclosing section titles.
  """
  stack = [(int(level), title) for level, title in initial_heading_list]
  for index, block in enumerate(block_list):
    block['id'] = index
    if block['type'] == 'heading':
      level = int(block.get('level') or 1)
      while stack and stack[-1][0] >= level:
        stack.pop()
      stack.append((level, block['text']))
    block['section_path'] = [title for _, title in stack]
  return block_list


def granulateBlockList(block_list, strategy='structure',
                       max_chars=DEFAULT_MAX_CHARS,
                       overlap_chars=DEFAULT_OVERLAP_CHARS,
                       include_tables=True, initial_heading_list=()):
  """Return the list of grains for ``block_list``.

  strategy:
    ``structure``  new grain at every heading, tables are kept apart
    ``page``       new grain at every page break (documents with pages)
    ``fixed``      structure is ignored, grains are cut every ``max_chars``
    ``blocks``     no packing, the annotated blocks are returned

  A grain is a dict with ``index``, ``text``, ``context`` (enclosing section
  titles), ``type`` ("text" or "table"), ``block_ids``, ``char_count``,
  ``content_hash`` (sha256 of ``text``) and, for documents with pages,
  ``page_start`` / ``page_end`` (pages of the blocks that contributed new
  text, not of the overlap).
  """
  block_list = annotateBlockList(block_list, initial_heading_list)
  if strategy == 'blocks':
    return [block for block in block_list
            if include_tables or block['type'] != 'table']
  packer = _Packer(max_chars, overlap_chars,
                   break_on_heading=strategy == 'structure',
                   break_on_page=strategy == 'page',
                   standalone_tables=strategy in ('structure', 'page'))
  for block in block_list:
    if block['type'] == 'table' and not include_tables:
      continue
    packer.add(block)
  return packer.finish()


class _Grain:
  def __init__(self, section_path, overlap=''):
    self.section_path = section_path
    self.overlap = overlap
    self.body = ''
    self.block_id_list = []
    self.page_list = []

  def text(self):
    if self.overlap:
      return self.overlap + '\n' + self.body
    return self.body

  def add(self, piece, block):
    self.body = self.body + BLOCK_SEPARATOR + piece if self.body else piece
    if block['id'] not in self.block_id_list:
      self.block_id_list.append(block['id'])
    if 'page' in block:
      self.page_list.append(block['page'])


class _Packer:
  def __init__(self, max_chars, overlap_chars, break_on_heading,
               break_on_page, standalone_tables):
    self.max_chars = max_chars
    self.overlap_chars = overlap_chars
    # room left for new text once the overlap has been prepended
    self.piece_limit = max_chars - overlap_chars - 1
    self.break_on_heading = break_on_heading
    self.break_on_page = break_on_page
    self.standalone_tables = standalone_tables
    self.grain_list = []
    self.current = None
    self.carry = ''

  def add(self, block):
    if block['type'] == 'table' and self.standalone_tables:
      self._flush(carry=False)
      for text in _splitTable(block['text'], self.max_chars):
        self._emit(text, block['section_path'], [block['id']],
                   [block['page']] if 'page' in block else [], 'table')
      return
    if block['type'] == 'heading' and self.break_on_heading:
      self._flush(carry=False)
    elif (self.break_on_page and self.current is not None and
          self.current.page_list and 'page' in block and
          block['page'] != self.current.page_list[-1]):
      self._flush(carry=False)
    for piece in _splitText(block['text'], self.piece_limit):
      if (self.current is not None and
          len(self.current.text()) + len(BLOCK_SEPARATOR) + len(piece)
          > self.max_chars):
        self._flush(carry=True)
      if self.current is None:
        self.current = _Grain(block['section_path'], self.carry)
        self.carry = ''
      self.current.add(piece, block)

  def finish(self):
    self._flush(carry=False)
    return self.grain_list

  def _flush(self, carry):
    grain, self.current = self.current, None
    self.carry = ''
    if grain is None:
      return
    text = grain.text()
    self._emit(text, grain.section_path, grain.block_id_list,
               grain.page_list, 'text')
    if carry:
      self.carry = _tail(text, self.overlap_chars)

  def _emit(self, text, section_path, block_id_list, page_list, kind):
    grain = {
      'index': len(self.grain_list),
      'text': text,
      'context': CONTEXT_SEPARATOR.join(section_path),
      'type': kind,
      'block_ids': list(block_id_list),
      'char_count': len(text),
      'content_hash': sha256(text.encode('utf-8')).hexdigest(),
    }
    if page_list:
      grain['page_start'] = min(page_list)
      grain['page_end'] = max(page_list)
    self.grain_list.append(grain)


def _cut(text, limit):
  """Cut ``text`` in two at the last whitespace before ``limit``."""
  index = text.rfind(' ', limit // 2, limit + 1)
  if index <= 0:
    index = limit
  return text[:index].rstrip(), text[index:].lstrip()


def _splitText(text, limit):
  """Split ``text`` in pieces of at most ``limit`` chars, on sentence
  boundaries when possible."""
  if len(text) <= limit:
    return [text]
  piece_list, current = [], ''
  for sentence in _SENTENCE_BOUNDARY_RE.split(text):
    while len(sentence) > limit:
      if current:
        piece_list.append(current)
        current = ''
      head, sentence = _cut(sentence, limit)
      piece_list.append(head)
    if not sentence:
      continue
    if current and len(current) + 1 + len(sentence) > limit:
      piece_list.append(current)
      current = sentence
    else:
      current = current + ' ' + sentence if current else sentence
  if current:
    piece_list.append(current)
  return piece_list


def _splitTable(text, max_chars):
  """Split a table (one row per line) on row boundaries, repeating the first
  row (header) on each part."""
  if len(text) <= max_chars:
    return [text]
  row_list = text.split('\n')
  header = row_list[0]
  part_list, current = [], [header]
  for row in row_list[1:]:
    for piece in _splitText(row, max_chars - len(header) - 1):
      if len(current) > 1 and \
          len('\n'.join(current)) + 1 + len(piece) > max_chars:
        part_list.append('\n'.join(current))
        current = [header]
      current.append(piece)
  if len(current) > 1 or not part_list:
    part_list.append('\n'.join(current))
  return part_list


def _tail(text, size):
  """Return the end of ``text`` (at most ``size`` chars) starting at a
  sentence or word boundary, to be used as overlap with the next grain."""
  if size <= 0 or len(text) <= size:
    return ''
  tail = text[-size:]
  match = _SENTENCE_BOUNDARY_RE.search(tail) or _WHITESPACE_RE.search(tail)
  if match is None:
    return ''
  return tail[match.end():].strip()
