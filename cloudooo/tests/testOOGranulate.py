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

import unittest
from zipfile import ZipFile
from StringIO import StringIO
from cloudoooTestCase import cloudoooTestCase, make_suite
from cloudooo.granulate.oogranulate import OOGranulate


class TestOOGranulate(cloudoooTestCase):

  def setUp(self):
    data = open('./data/granulate_test.odt').read()
    self.oogranulate = OOGranulate(data, 'odt')

  def testGetElementsByTagName(self):
    """Test if _getElementsByTagName() returns right elements list"""
    element_list = self.oogranulate._getElementsByTagName(
                                      self.oogranulate.document.parsed_content,
                                      'draw:image')
    self.assertEquals(len(element_list), 5)
    for element in element_list:
      self.assertTrue(element.tag.endswith('image'))

  def testHasAncertor(self):
    """_hasAncestor() should vefify if the elements has the ancestor or not"""
    image_list = self.oogranulate._getElementsByTagName(
                                      self.oogranulate.document.parsed_content,
                                      'draw:image')
    self.assertFalse(self.oogranulate._hasAncestor(image_list[0], 'text-box'))
    self.assertTrue(self.oogranulate._hasAncestor(image_list[0], 'frame'))
    self.assertTrue(self.oogranulate._hasAncestor(image_list[2], 'text-box'))

  def testGetImageTitle(self):
    """_hasAncestor() should vefify if the elements has the ancestor or not"""
    image_list = self.oogranulate._getElementsByTagName(
                                      self.oogranulate.document.parsed_content,
                                      'draw:image')
    self.assertEquals(self.oogranulate._getImageTitle(image_list[0]), '')
    self.assertEquals(self.oogranulate._getImageTitle(image_list[2]),
                                                'Illustration 1: TioLive Logo')

  def testgetTableItemList(self):
    """Test if getTableItemList() returns the right tables list"""
    self.assertRaises(NotImplementedError, self.oogranulate.getTableItemList,
                                           'file')

  def testGetColumnItemList(self):
    """Test if getColumnItemList() returns the right table columns list"""
    self.assertRaises(NotImplementedError, self.oogranulate.getColumnItemList,
                                     'file',
                                     'table_id')

  def testGetLineItemList(self):
    """Test if getLineItemList() returns the right table lines list"""
    self.assertRaises(NotImplementedError, self.oogranulate.getLineItemList,
                                     'file',
                                     'table_id')

  def testGetImageItemList(self):
    """Test if getImageItemList() returns the right images list"""
    image_list = self.oogranulate.getImageItemList()
    self.assertEquals([
      ('10000000000000C80000009C38276C51.jpg', ''),
      ('10000201000000C80000004E7B947D46.png', ''),
      ('10000201000000C80000004E7B947D46.png', 'Illustration 1: TioLive Logo'),
      # XXX The svg image are stored into odf as svm
      ('2000004F00004233000013707E7DE37A.svm', 'Figure 1: Python Logo'),
      ('10000201000000C80000004E7B947D46.png',
        'Illustration 2: Again TioLive Logo'),
      ], image_list)

  def testGetImageSuccessfully(self):
    """Test if getImage() returns the right image file successfully"""
    data = open('./data/granulate_test.odt').read()
    zip = ZipFile(StringIO(data))
    image_id = '10000000000000C80000009C38276C51.jpg'
    original_image = zip.read('Pictures/%s' % image_id)
    geted_image = self.oogranulate.getImage(image_id)
    self.assertEquals(original_image, geted_image)

  def testGetImageWithoutSuccess(self):
    """Test if getImage() returns an empty string for not existent id"""
    geted_image = self.oogranulate.getImage('anything.png')
    self.assertEquals('', geted_image)

  def testGetParagraphItemList(self):
    """Test if getParagraphItemList() returns the right paragraphs list"""
    self.assertRaises(NotImplementedError,
                      self.oogranulate.getParagraphItemList,
                      'file')

  def testGetParagraphItem(self):
    """Test if getParagraphItem() returns the right paragraph"""
    self.assertRaises(NotImplementedError, self.oogranulate.getParagraphItem,
                                     'file',
                                     'paragraph_id')

  def testGetChapterItemList(self):
    """Test if getChapterItemList() returns the right chapters list"""
    self.assertRaises(NotImplementedError, self.oogranulate.getChapterItemList,
                                           'file')

  def testGetChapterItem(self):
    """Test if getChapterItem() returns the right chapter"""
    self.assertRaises(NotImplementedError, self.oogranulate.getChapterItem,
                                     'file',
                                     'chapter_id')


def test_suite():
  return make_suite(TestOOGranulate)

if __name__ == "__main__":
  suite = unittest.TestLoader().loadTestsFromTestCase(TestOOGranulate)
  unittest.TextTestRunner(verbosity=2).run(suite)
