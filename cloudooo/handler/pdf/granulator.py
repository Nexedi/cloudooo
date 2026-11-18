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

import os
import re
import subprocess
import tempfile
from io import BytesIO

from pypdf import PdfReader

from cloudooo.grain import GranulateError
from cloudooo.util import logger

PDFTOTEXT_TIMEOUT = 600

_PARAGRAPH_SEPARATOR_RE = re.compile(r'\n[ \t]*\n')


class PdfGranulator:
  """Extract the text of a PDF as a list of blocks (headings, paragraphs)
  carrying their page number, for use by ``cloudooo.grain``.

  Text comes from ``pdftotext`` (one process for the requested pages) and the
  section titles from the PDF outline (bookmarks). Without an outline there
  are no headings. Pages without a text layer (scans) produce no block, there
  is no OCR. Tables are not detected, their text is returned as paragraphs.
  """

  def __init__(self, data: bytes, base_folder_url=None, env=None,
               timeout=PDFTOTEXT_TIMEOUT):
    self._data = data
    self._base_folder_url = base_folder_url
    self._env = env or None
    self._timeout = timeout
    try:
      self._reader = PdfReader(BytesIO(data))
      if self._reader.is_encrypted and not self._reader.decrypt(''):
        raise GranulateError('PDF is encrypted and needs a password')
      self.page_count = len(self._reader.pages)
    except GranulateError:
      raise
    except Exception as e:
      raise GranulateError('Invalid PDF document: %s' % e)
    self._outline_list = None

  def getPageCount(self) -> int:
    return self.page_count

  def _getOutlineList(self):
    """Returns [(level, title, page_number)] in document order, pages
    start at 1."""
    if self._outline_list is not None:
      return self._outline_list
    outline_list = []

    def walk(item_list, level):
      for item in item_list:
        if isinstance(item, list):
          walk(item, level + 1)
          continue
        try:
          page_index = self._reader.get_destination_page_number(item)
          title = ' '.join(str(item.title).split())
        except Exception:
          continue
        if page_index is None or page_index < 0 or not title:
          continue
        outline_list.append((level, title, page_index + 1))

    try:
      walk(self._reader.outline, 1)
    except Exception:
      logger.warning('PDF outline can not be read', exc_info=True)
    self._outline_list = outline_list
    return outline_list

  def getOutlineContext(self, first_page=None):
    """Returns [(level, title)] of the headings open when ``first_page``
    starts, the outline being what defines them."""
    first_page = first_page or 1
    return [(level, title)
            for level, title, page in self._getOutlineList()
            if page < first_page]

  def _checkPageRange(self, first_page, last_page):
    first_page = first_page or 1
    last_page = min(last_page or self.page_count, self.page_count)
    if first_page > self.page_count:
      raise GranulateError(
        'page_range starts at page %s but the document has %s page(s)' %
        (first_page, self.page_count))
    return first_page, last_page

  def _getPageTextList(self, first_page, last_page):
    folder = self._base_folder_url
    with tempfile.TemporaryDirectory(dir=folder) as directory:
      pdf_path = os.path.join(directory, 'document.pdf')
      with open(pdf_path, 'wb') as f:
        f.write(self._data)
      command = ['pdftotext', '-q', '-enc', 'UTF-8',
                 '-f', str(first_page), '-l', str(last_page), pdf_path, '-']
      try:
        result = subprocess.run(
          command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
          close_fds=True, env=self._env, timeout=self._timeout)
      except subprocess.TimeoutExpired:
        raise GranulateError(
          'pdftotext timed out after %s seconds' % self._timeout)
      except OSError as e:
        raise GranulateError('pdftotext can not be run: %s' % e)
    if result.returncode != 0:
      raise GranulateError('pdftotext failed (%s): %s' % (
        result.returncode, result.stderr.decode('utf-8', 'replace').strip()))
    # pdftotext terminates every page with a form feed
    text_list = result.stdout.decode('utf-8', 'replace').split('\f')
    expected = last_page - first_page + 1
    text_list = text_list[:expected]
    text_list += [''] * (expected - len(text_list))
    return text_list

  def getBlockList(self, first_page=None, last_page=None):
    """Returns the blocks of pages ``first_page`` to ``last_page`` (both
    included, starting at 1; defaults to the whole document)."""
    first_page, last_page = self._checkPageRange(first_page, last_page)
    outline_list = self._getOutlineList()
    block_list = []
    for page, text in enumerate(
        self._getPageTextList(first_page, last_page), first_page):
      item_list = [
        {'type': 'paragraph', 'line_list': line_list}
        for line_list in (
          [line.strip() for line in part.split('\n') if line.strip()]
          for part in _PARAGRAPH_SEPARATOR_RE.split(text))
        if line_list]
      if not item_list:
        logger.warning('PDF page %s has no text layer', page)
      for level, title, outline_page in outline_list:
        if outline_page == page:
          _insertHeading(item_list, level, title)
      for item in item_list:
        if item['type'] == 'heading':
          block = {'type': 'heading', 'level': item['level'],
                   'text': item['text'], 'page': page}
        else:
          block = {'type': 'paragraph', 'page': page,
                   'text': _joinLineList(item['line_list'])}
        if block['text']:
          block_list.append(block)
    return block_list


def _insertHeading(item_list, level, title):
  """Mark the paragraph that starts with ``title`` as a heading, or add a
  heading at the top of the page if the title is not found in its text."""
  wanted = title.lower()
  heading = {'type': 'heading', 'level': level, 'text': title}
  for index, item in enumerate(item_list):
    if item['type'] != 'paragraph':
      continue
    line_list = item['line_list']
    for count in range(1, min(3, len(line_list)) + 1):
      if ' '.join(line_list[:count]).lower() == wanted:
        rest = line_list[count:]
        item_list[index:index + 1] = [heading] + (
          [{'type': 'paragraph', 'line_list': rest}] if rest else [])
        return
  # not found: keep it after headings already added at the top of the page
  position = 0
  while position < len(item_list) and item_list[position]['type'] == 'heading':
    position += 1
  item_list.insert(position, heading)


def _joinLineList(line_list):
  """Join the hard wrapped lines of a paragraph. A word split with a hyphen
  at the end of a line is joined back when the next line continues in
  lowercase (this also affects compounds such as ``state-of-`` / ``the-art``).
  """
  text = ''
  for line in line_list:
    if (len(text) > 1 and text.endswith('-') and text[-2].isalpha() and
        line[:1].islower()):
      text = text[:-1] + line
    else:
      text = text + ' ' + line if text else line
  return text
