#############################################################################
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
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################

from zipfile import ZipFile
from io import BytesIO
from lxml import etree
from os import path
from cloudooo.util import logger
from cloudooo.handler.ooo.document import OdfDocument

# URI Definitions.
TEXT_URI = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
TABLE_URI = 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
DRAWING_URI = 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'

# Odf Namespaces
TABLE_ATTRIB_NAME = '{%s}name' % TABLE_URI
TEXT_ATTRIB_STYLENAME = '{%s}style-name' % TEXT_URI
DRAWING_ATTRIB_STYLENAME = '{%s}style-name' % DRAWING_URI
DRAWING_ATTRIB_NAME = '{%s}name' % DRAWING_URI

# XPath queries for ODF format
RELEVANT_PARAGRAPH_XPATH_QUERY = '//text:p[not(ancestor::draw:frame)]'
DRAW_XPATH_QUERY = './/draw:image'
TABLE_XPATH_QUERY = './/table:table'
IMAGE_TITLE_XPATH_QUERY = '//draw:text-box/text:p/draw:frame[@draw:style-name="%s"][@draw:name="%s"]/draw:image[@xlink:href="Pictures/%s"]/ancestor::draw:frame/following-sibling::text()'
IMAGE_DRAW_NAME_AND_STYLENAME_XPATH_QUERY = '//draw:text-box/text:p/draw:frame'
CHAPTER_XPATH_QUERY = '//text:p[@text:style-name="Title"]/text:span/text() | //text:h/text:span/text()'

def getTemplatePath(format):
  """ Get the path of template file. This should goes to
      some utils library.
  """
  return path.join(path.dirname(__file__), 'template.%s' % format)


class OOGranulator:
  """Granulate an OpenOffice document into tables, images, chapters and
  paragraphs."""

  def __init__(self, file:bytes, source_format:str):
    self.document = OdfDocument(file, source_format)

  def _odfWithoutContentXml(self, format='odt'):
    """Returns an odf document without content.xml
    It is a way to escape from this issue: http://bugs.python.org/issue6818"""
    new_odf_document = ZipFile(BytesIO(), 'a')
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
      if title == '':
        title = ''.join(table.xpath('following-sibling::text:p[position()=1] \
                    [starts-with(@text:style-name, "Tabela")]//text()',
                    namespaces=table.nsmap))
      id = table.attrib[TABLE_ATTRIB_NAME]
      table_list.append((id, title))
    return table_list

  def getTable(self, id, format='odt'):
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
      # Next line do this
      # <office:content><office:body><office:text><table:table>
      content_xml[-1][0].append(table)
      # XXX: Next line replace the <office:automatic-styles> tag. This include
      # a lot of unused style tags. Will be better detect the used styles and
      # include only those.
      content_xml.replace(content_xml[-2],
                          self.document.parsed_content[-2])

      odf_document = self._odfWithoutContentXml(format)
      odf_document.writestr('content.xml', etree.tostring(content_xml))
      odf_document_as_string = odf_document.fp
      odf_document.close()
      odf_document_as_string.seek(0)
      return odf_document_as_string.read()
    except Exception as e:
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

  def getColumnItemList(self, table_id):
    """Return the list of columns in the form of (id, title)."""
    row_list = self.document.parsed_content.xpath(
                 '//table:table[@table:name="%s"]/table:table-row' % table_id,
                 namespaces=self.document.parsed_content.nsmap)

    if len(row_list) == 0:
      return None
    id = 0
    columns = []
    for cell in row_list[0].iterchildren():
      columns.append([id,''.join(cell.itertext())])
      id+=1
    return columns

  def getLineItemList(self, table_id):
    """Returns the lines of a given table as (key, value) pairs."""
    row_list = self.document.parsed_content.xpath(
                 '//table:table[@table:name="%s"]/table:table-row' % table_id,
                 namespaces=self.document.parsed_content.nsmap)

    if len(row_list) == 0:
      return None

    matrix = []
    fields = []
    for cell_key in row_list[0].iterchildren():
      fields.append(''.join(cell_key.itertext()))
    for row_values in row_list[1::]:
      for cell in row_values.iterchildren():
        matrix.append([fields[0], ''.join(cell.itertext())])
        fields+=[fields[0]]
        fields.remove(fields[0])
    return matrix

  #this function will be use to pick up the attibutes name and style-name
  def _getFrameImageList(self):
    relevant_image_list = self.document.parsed_content.xpath(
                                 IMAGE_DRAW_NAME_AND_STYLENAME_XPATH_QUERY,
                                 namespaces=self.document.parsed_content.nsmap)

    return relevant_image_list

  def getImageItemList(self):
    """Return a list of tuples with the id and title of image files"""
    xml_image_list = self.document.parsed_content.xpath(DRAW_XPATH_QUERY,
                                namespaces=self.document.parsed_content.nsmap)
    name_list = []
    stylename_list = []
    for i in self._getFrameImageList():
      name_list.append(i.attrib[DRAWING_ATTRIB_NAME])
      stylename_list.append(i.attrib[DRAWING_ATTRIB_STYLENAME])

    image_list = []

    for xml_image in xml_image_list:
      id = list(xml_image.values())[0].split('/')[-1]
      title = ''.join(xml_image.xpath(IMAGE_TITLE_XPATH_QUERY%(stylename_list[0], name_list[0], id),
                                      namespaces=xml_image.nsmap))
      if title != '':
        title_list = title.split(':')
        title = ''.join(title_list[1:])
        title = title.strip()
        name_list.pop(0)
        stylename_list.pop(0)

      image_list.append((id, title))
    
    return image_list

  def getImage(self, id, format=None, resolution=None, **kw):
    """Return the given image."""
    path = 'Pictures/%s' % id
    return self.document.getFile(path)

  def _getRelevantParagraphList(self):
    relevant_paragraph_list = self.document.parsed_content.xpath(
                                 RELEVANT_PARAGRAPH_XPATH_QUERY,
                                 namespaces=self.document.parsed_content.nsmap)

    return relevant_paragraph_list

  def getParagraphItemList(self):
    """Returns the list of paragraphs in the form of (id, class) where class
    may have special meaning to define TOC/TOI."""
    id = 0
    paragraph_list = []
    for p in self._getRelevantParagraphList():
      paragraph_list.append((id, p.attrib[TEXT_ATTRIB_STYLENAME]))
      id += 1
    return paragraph_list

  def getParagraph(self, paragraph_id):
    """Returns the paragraph in the form of (text, class)."""
    relevant_paragraph_list = self._getRelevantParagraphList()
    try:
      paragraph = relevant_paragraph_list[paragraph_id]
    except IndexError:
      msg = "Unable to find paragraph %s at paragraph list." % paragraph_id
      logger.error(msg)
      return None

    text = ''.join(paragraph.itertext())

    if TEXT_ATTRIB_STYLENAME not in paragraph.attrib:
      logger.error("Unable to find %s attribute at paragraph %s ",
                              TEXT_ATTRIB_STYLENAME, paragraph_id)
      return None

    p_class = paragraph.attrib[TEXT_ATTRIB_STYLENAME]
    return (text, p_class)

  def _getChapterList(self):
    chapter_list = self.document.parsed_content.xpath(
                                 CHAPTER_XPATH_QUERY,
                                 namespaces=self.document.parsed_content.nsmap)
    return [str(x) for x in chapter_list]

  def getChapterItemList(self):
    """Returns the list of chapters in the form of (id, level)."""
    return list(enumerate(self._getChapterList()))

  def getChapterItem(self, chapter_id):
    """Return the chapter in the form of (title, level)."""
    chapter_list = self._getChapterList()
    try:
      chapter = chapter_list[chapter_id]
      return [chapter, chapter_id]
    except IndexError:
      msg = "Unable to find chapter %s at chapter list." % chapter_id
      logger.error(msg)
      return None

  def trash(self):
    """Remove the file in memory."""
    self.document.trash()
