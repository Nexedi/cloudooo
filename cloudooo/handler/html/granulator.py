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
"""Extract readable text from HTML as blocks for ``cloudooo.grain``."""

from lxml import etree, html

from cloudooo.grain import GranulateError, TABLE_CELL_SEPARATOR

HEADING_TAG_SET = frozenset('h%s' % level for level in range(1, 7))

# Content that is not part of the readable text of the document.
SKIP_TAG_SET = frozenset((
  'head', 'script', 'style', 'noscript', 'template', 'iframe', 'object',
  'embed', 'svg', 'canvas', 'audio', 'video'))

# Tags turned into a block of their own. Other tags are containers whose
# loose text is gathered into paragraphs.
BLOCK_TAG_SET = HEADING_TAG_SET | frozenset((
  'p', 'li', 'blockquote', 'pre', 'dt', 'dd', 'figcaption'))

# Tags allowed below a list item: nested lists and tables are extracted as
# separate blocks, inline markup has already been included in the item text.
NESTED_BLOCK_TAG_SET = BLOCK_TAG_SET | frozenset((
  'ul', 'ol', 'dl', 'table', 'div', 'section', 'article'))


def _localname(tag):
  if not isinstance(tag, str):
    return ''  # comments and processing instructions
  return tag.rsplit('}', 1)[-1].lower()


def _isBlockTag(tag):
  return tag in SKIP_TAG_SET or tag in BLOCK_TAG_SET or tag == 'table'


def _containsBlock(element):
  """Whether an element contains a block which must be extracted on its own."""
  return any(_isBlockTag(_localname(child.tag))
             for child in element.iterdescendants())


def _normalise(part_list):
  """Collapse whitespace (including non-breaking spaces), keeping line breaks."""
  text = ''.join(part_list).replace('\xa0', ' ')
  return '\n'.join(' '.join(line.split()) for line in text.split('\n')).strip()


def _getElementText(element):
  """Text of an element, without the text of nested blocks or scripts."""
  part_list = []

  def visit(parent):
    if parent.text:
      part_list.append(parent.text)
    for child in parent:
      tag = _localname(child.tag)
      if tag == 'br':
        part_list.append('\n')
      elif tag in SKIP_TAG_SET or tag in NESTED_BLOCK_TAG_SET:
        continue
      else:
        visit(child)
      if child.tail:
        part_list.append(child.tail)

  visit(element)
  return _normalise(part_list)


def _getTableText(table):
  """One line per row, cells separated by ``TABLE_CELL_SEPARATOR``."""
  line_list = []
  for row in table.iter():
    if _localname(row.tag) != 'tr':
      continue
    cell_list = [' '.join(_getElementText(cell).split())
                 for cell in row
                 if _localname(cell.tag) in ('td', 'th')]
    while cell_list and not cell_list[-1]:
      cell_list.pop()
    if cell_list:
      line_list.append(TABLE_CELL_SEPARATOR.join(cell_list))
  return '\n'.join(line_list)


def _append(block_list, block_type, text, **kw):
  if text:
    block_list.append({'type': block_type, 'text': text, **kw})


class HtmlGranulator:
  """Read an HTML document as a list of blocks in reading order.

  Headings keep their outline level, list items and tables are separate
  blocks, and non-readable markup (scripts, styles, head, ...) is ignored.
  HTML has no page information, so blocks carry no ``page`` key.
  """

  def __init__(self, data: bytes):
    self._data = data
    self._root = None

  def _getRoot(self):
    if self._root is None:
      try:
        self._root = html.fromstring(self._data)
      except (etree.ParserError, ValueError) as e:
        raise GranulateError('Invalid HTML document: %s' % e)
    return self._root

  def getBlockList(self):
    block_list = []
    self._walk(self._getRoot(), block_list)
    return block_list

  def _walk(self, element, block_list):
    tag = _localname(element.tag)
    if tag in SKIP_TAG_SET:
      return
    if tag in HEADING_TAG_SET:
      _append(block_list, 'heading', _getElementText(element),
              level=int(tag[1]))
      return
    if tag == 'table':
      _append(block_list, 'table', _getTableText(element))
      return
    if tag in BLOCK_TAG_SET:
      _append(block_list,
              'list_item' if tag == 'li' else 'paragraph',
              _getElementText(element))
      if tag == 'li':
        # Nested lists and tables belong to separate blocks.
        for child in element:
          if _localname(child.tag) in NESTED_BLOCK_TAG_SET:
            self._walk(child, block_list)
      return
    self._walkContainer(element, block_list)

  def _walkContainer(self, element, block_list):
    """Walk children, gathering text which is not inside a block as a
    paragraph, and flushing it before each block to keep reading order."""
    part_list = [element.text] if element.text else []
    for child in element:
      if _isBlockTag(_localname(child.tag)) or _containsBlock(child):
        self._flushText(part_list, block_list)
        self._walk(child, block_list)
      else:
        # Inline markup belongs to the current paragraph, including the text
        # of nested inline elements and the tail of this element.
        part_list.append(_getElementText(child))
      if child.tail:
        part_list.append(child.tail)
    self._flushText(part_list, block_list)

  @staticmethod
  def _flushText(part_list, block_list):
    text = _normalise(part_list)
    if text:
      _append(block_list, 'paragraph', text)
    part_list.clear()
