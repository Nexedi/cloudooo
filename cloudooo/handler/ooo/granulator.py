##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Hugo H. Maia Vieira <hugomaia@tiolive.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from zope.interface import implements
from zipfile import ZipFile
from StringIO import StringIO
from lxml import etree
from os import path
from cloudooo.utils.utils import logger
from cloudooo.handler.ooo.document import OdfDocument
from cloudooo.interfaces.granulate import ITableGranulator, \
                                          IImageGranulator, \
                                          ITextGranulator

# URI Definitions.
TEXT_URI = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
TABLE_URI = 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'

# Odf Namespaces
TABLE_ATTRIB_NAME = '{%s}name' % TABLE_URI
TEXT_ATTRIB_STYLENAME = '{%s}style-name' % TEXT_URI

# XPath queries for ODF format
RELEVANT_PARAGRAPH_XPATH_QUERY = '//text:p[not(ancestor::draw:frame)]'
DRAW_XPATH_QUERY = './/draw:image'
TABLE_XPATH_QUERY = './/table:table'
IMAGE_TITLE_XPATH_QUERY = './/../../text() | .//../../*/text()'

def getTemplatePath(format):
  """ Get the path of template file. This should goes to
      some utils library.
  """
  return path.join(path.dirname(__file__), 'template.%s' % format)

class OOGranulator(object):
  """Granulate an OpenOffice document into tables, images, chapters and
  paragraphs."""

  implements(ITableGranulator, IImageGranulator, ITextGranulator)

  def __init__(self, file, source_format):
    self.document = OdfDocument(file, source_format)

  def _odfWithoutContentXml(self, format='odt'):
    """Returns an odf document without content.xml
    It is a way to escape from this issue: http://bugs.python.org/issue6818"""
    new_odf_document = ZipFile(StringIO(), 'a')
    template_path = getTemplatePath(format)
    template_file = ZipFile(template_path)
    for item in template_file.filelist:
      buffer = template_file.read(item.filename)
      if item.filename != 'content.xml':
        new_odf_document.writestr(item.filename, buffer)
    template_file.close()
    return new_odf_document

  def getTableItemList(self):
    """Returns the list of table IDs in the form of (id, title)."""
    xml_table_list = self.document.parsed_content.xpath(TABLE_XPATH_QUERY,
                                namespaces=self.document.parsed_content.nsmap)
    table_list = []
    for table in xml_table_list:
      title = ''.join(table.xpath('following-sibling::text:p[position()=1] \
                          [starts-with(@text:style-name, "Table")]//text()',
                          namespaces=table.nsmap))
      id = table.attrib[TABLE_ATTRIB_NAME]
      table_list.append((id, title))
    return table_list

  def getTableItem(self, id, format='odt'):
    """Returns the table into a new 'format' file."""
    try:
      template_path = getTemplatePath(format)
      template = ZipFile(template_path)
      content_xml = etree.fromstring(template.read('content.xml'))
      template.close()
      table_list = self.document.parsed_content.xpath(
                                '//table:table[@table:name="%s"]' % id,
                                namespaces=self.document.parsed_content.nsmap)
      if len(table_list) == 0:
        return None
      table = table_list[0]
      # Next line do this <office:content><office:body><office:text><table:table>
      content_xml[-1][0].append(table)
      # XXX: Next line replace the <office:automatic-styles> tag. This include a
      #      lot of unused style tags. Will be better detect the used styles and
      #      include only those.
      content_xml.replace(content_xml[-2],
                          self.document.parsed_content[-2])

      odf_document = self._odfWithoutContentXml(format)
      odf_document.writestr('content.xml', etree.tostring(content_xml))
      odf_document_as_string = odf_document.fp
      odf_document.close()
      odf_document_as_string.seek(0)
      return odf_document_as_string.read()
    except Exception, e:
      logger.error(e)
      return None

  def getTableMatrix(self, id):
    """Returns the table as a matrix"""
    row_list = self.document.parsed_content.xpath(
                        '//table:table[@table:name="%s"]/table:table-row' % id,
                        namespaces=self.document.parsed_content.nsmap)
    if len(row_list) == 0:
      return None

    matrix = []
    for row in row_list:
      matrix_row = []
      for cell in row.iterchildren():
        matrix_row.append(''.join(cell.itertext()))
      matrix.append(matrix_row)
    return matrix


  def getColumnItemList(self, file, table_id):
    """Return the list of columns in the form of (id, title)."""
    raise NotImplementedError

  def getLineItemList(self, file, table_id):
    """Returns the lines of a given table as (key, value) pairs."""
    raise NotImplementedError

  def getImageItemList(self):
    """Return a list of tuples with the id and title of image files"""
    xml_image_list = self.document.parsed_content.xpath(DRAW_XPATH_QUERY,
                                namespaces=self.document.parsed_content.nsmap)

    image_list = []
    for xml_image in xml_image_list:
      title = ''.join(xml_image.xpath(IMAGE_TITLE_XPATH_QUERY,
                                      namespaces=xml_image.nsmap))
      id = xml_image.values()[0].split('/')[-1]
      image_list.append((id, title))
    return image_list

  def getImage(self, id, format=None, resolution=None, **kw):
    """Return the given image."""
    path = 'Pictures/%s' % id
    return self.document.getFile(path)

  def _getRelevantParagraphList(self):
    """ This should use memcache or another cache infrastructure.
    """
    RELEVANT_PARAGRAPH_CACHE = getattr(self, "RELEVANT_PARAGRAPH_CACHE", None)
    if RELEVANT_PARAGRAPH_CACHE is None:
      relevant_paragraph_list = self.document.parsed_content.xpath(
                                 RELEVANT_PARAGRAPH_XPATH_QUERY,
                                 namespaces=self.document.parsed_content.nsmap)
      setattr(self, "RELEVANT_PARAGRAPH_CACHE", relevant_paragraph_list)

    return self.RELEVANT_PARAGRAPH_CACHE

  def getParagraphItemList(self):
    """Returns the list of paragraphs in the form of (id, class) where class
    may have special meaning to define TOC/TOI."""
    id = 0
    paragraph_list = []
    for p in self._getRelevantParagraphList():
      paragraph_list.append((id, p.attrib[TEXT_ATTRIB_STYLENAME]))
      id += 1
    return paragraph_list

  def getParagraphItem(self, paragraph_id):
    """Returns the paragraph in the form of (text, class)."""
    relevant_paragraph_list = self._getRelevantParagraphList()
    try:
      paragraph = relevant_paragraph_list[paragraph_id]
    except IndexError:
      logger.error("Unable to find paragraph %s at paragraph list." % paragraph_id)
      return None

    text = ''.join(paragraph.itertext())

    if TEXT_ATTRIB_STYLENAME not in paragraph.attrib.keys():
      logger.error("Unable to find %s attribute at paragraph %s " % \
                              (TEXT_ATTRIB_STYLENAME, paragraph_id))
      return None

    p_class = paragraph.attrib[TEXT_ATTRIB_STYLENAME]
    return (text, p_class)

  def getChapterItemList(self, file):
    """Returns the list of chapters in the form of (id, level)."""
    raise NotImplementedError

  def getChapterItem(self, file, chapter_id):
    """Return the chapter in the form of (title, level)."""
    raise NotImplementedError

  def trash(self):
    """Remove the file in memory."""
    self.document.trash()
