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
from cloudooo.tests.handlerTestCase import HandlerTestCase
from cloudooo.handler.ooo.granulator import OOGranulator


class TestOOGranulator(HandlerTestCase):

  def setUp(self):
    with open('./data/granulate_test.odt', 'rb') as f:
      data = f.read()
    self.oogranulator = OOGranulator(data, 'odt')

  def testOdfWithoutContentXml(self):
    """Test if _odfWithoutContentXml() return a ZipFile instance without the
    content.xml file"""
    odf_without_content_xml = self.oogranulator._odfWithoutContentXml('odt')
    self.assertTrue(isinstance(odf_without_content_xml, ZipFile))
    complete_name_list = []
    for item in self.oogranulator.document._zipfile.filelist:
      complete_name_list.append(item.filename)
    for item in odf_without_content_xml.filelist:
      self.assertTrue(item.filename in complete_name_list)
      self.assertTrue(item.filename != 'content.xml')

  def testgetTableItemList(self):
    """Test if getTableItemList() returns the right tables list"""
    with open('./data/granulate_table_test.odt', 'rb') as f:
      data = f.read()
    oogranulator = OOGranulator(data, 'odt')
    table_list = [('Developers', ''),
                  ('Prices', 'Table 1: Prices table from Mon Restaurant'),
                  ('SoccerTeams', 'Tabela 2: Soccer Teams')]
    self.assertEqual(table_list, oogranulator.getTableItemList())

  def testGetTable(self):
    """Test if getTable() returns on odf file with the right table"""
    with open('./data/granulate_table_test.odt', 'rb') as f:
      data = f.read()
    oogranulator = OOGranulator(data, 'odt')
    table_data_doc = oogranulator.getTable('Developers')
    content_xml_str = ZipFile(BytesIO(table_data_doc)).read('content.xml')
    content_xml = etree.fromstring(content_xml_str)
    table_list = content_xml.xpath('//table:table',
                                   namespaces=content_xml.nsmap)
    self.assertEqual(1, len(table_list))
    table = table_list[0]
    name_key = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name'
    self.assertEqual('Developers', table.attrib[name_key])

  def testGetTableItemWithoutSuccess(self):
    """Test if getTable() returns None for an non existent table name"""
    with open('./data/granulate_table_test.odt', 'rb') as f:
      data = f.read()
    oogranulator = OOGranulator(data, 'odt')
    table_data = oogranulator.getTable('NonExistentTable')
    self.assertEqual(table_data, None)

  def testGetColumnItemList(self):
    """Test if getColumnItemList() returns the right table columns list"""
    with open('./data/granulate_table_test.odt', 'rb') as f:
      data = f.read()
    oogranulator = OOGranulator(data, 'odt')
    self.assertEqual([[0, 'Name'], [1, 'Country']],
                      oogranulator.getColumnItemList('SoccerTeams'))

  def testGetLineItemList(self):
    """Test if getLineItemList() returns the right table lines list"""
    with open('./data/granulate_table_test.odt', 'rb') as f:
      data = f.read()
    oogranulator = OOGranulator(data, 'odt')
    matrix = [['Name', 'Phone', 'Email'],
             ['Hugo', '+55 (22) 8888-8888', 'hugomaia@tiolive.com'],
             ['Rafael', '+55 (22) 9999-9999', 'rafael@tiolive.com']]
    self.assertEqual(matrix, oogranulator.getTableMatrix('Developers'))

    matrix = [['Product', 'Price'],
             ['Pizza', 'R$ 25,00'],
             ['Petit Gateau', 'R$ 10,00'],
             ['Feijoada', 'R$ 30,00']]
    self.assertEqual(matrix, oogranulator.getTableMatrix('Prices'))

    self.assertEqual(None, oogranulator.getTableMatrix('Non existent'))

  def testGetImageItemList(self):
    """Test if getImageItemList() returns the right images list"""
    image_list = self.oogranulator.getImageItemList()
    self.assertEqual([('10000000000000C80000009C38276C51.jpg', ''),
                       ('10000201000000C80000004E7B947D46.png', 'TioLive Logo'),
                       ('10000201000000C80000004E7B947D46.png', ''),
                       # XXX The svg image are stored into odf as svm
                       ('2000004F00004233000013707E7DE37A.svm', 'Python Logo'),
                       ('10000201000000C80000004E7B947D46.png',
                        'Again TioLive Logo')], image_list)

  def testGetImageSuccessfully(self):
    """Test if getImage() returns the right image file successfully"""
    with open('./data/granulate_test.odt', 'rb') as f:
      data = f.read()
    zip = ZipFile(BytesIO(data))
    image_id = '10000000000000C80000009C38276C51.jpg'
    original_image = zip.read('Pictures/%s' % image_id)
    geted_image = self.oogranulator.getImage(image_id)
    self.assertEqual(original_image, geted_image)

  def testGetImageWithoutSuccess(self):
    """Test if getImage() returns an empty string for not existent id"""
    obtained_image = self.oogranulator.getImage('anything.png')
    self.assertEqual(b'', obtained_image)

  def testGetParagraphItemList(self):
    """Test if getParagraphItemList() returns the right paragraphs list, with
    the ids always in the same order"""
    for _ in range(5):
      with open('./data/granulate_test.odt', 'rb') as f:
        data = f.read()
      oogranulator = OOGranulator(data, 'odt')
      paragraph_list = oogranulator.getParagraphItemList()
      self.assertEqual((0, 'P3'), paragraph_list[0])
      self.assertEqual((1, 'P1'), paragraph_list[1])
      self.assertEqual((2, 'P12'), paragraph_list[2])
      self.assertEqual((8, 'P13'), paragraph_list[8])
      self.assertEqual((19, 'Standard'), paragraph_list[19])

  def testGetParagraphItemSuccessfully(self):
    """Test if getParagraphItem() returns the right paragraph"""
    self.assertEqual(('Some images without title', 'P13'),
                      self.oogranulator.getParagraph(8))

    big_paragraph = self.oogranulator.getParagraph(5)
    self.assertEqual('P8', big_paragraph[1])
    self.assertTrue(big_paragraph[0].startswith('A prática cotidiana prova'))
    self.assertTrue(big_paragraph[0].endswith('corresponde às necessidades.'))

  def testGetParagraphItemWithoutSuccess(self):
    """Test if getParagraphItem() returns None for not existent id"""
    self.assertEqual(None, self.oogranulator.getParagraph(200))

  def testGetChapterItemList(self):
    """Test if getChapterItemList() returns the right chapters list"""
    with open('./data/granulate_chapters_test.odt', 'rb') as f:
      data = f.read()
    oogranulator = OOGranulator(data, 'odt')
    self.assertEqual([(0, 'Title 0'), (1, 'Title 1'), (2, 'Title 2'),
                       (3, 'Title 3'), (4, 'Title 4'), (5, 'Title 5'),
                       (6, 'Title 6'), (7, 'Title 7'), (8, 'Title 8'),
                       (9, 'Title 9'), (10, 'Title 10')],
                                          oogranulator.getChapterItemList())

  def testGetChapterItem(self):
    """Test if getChapterItem() returns the right chapter"""
    with open("./data/granulate_chapters_test.odt", 'rb') as f:
      data = f.read()
    oogranulator = OOGranulator(data, 'odt')
    self.assertEqual(['Title 1', 1], oogranulator.getChapterItem(1))

