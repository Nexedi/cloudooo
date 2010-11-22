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
from cloudoooTestCase import cloudoooTestCase, make_suite
from cloudooo.granulate.oogranulate import OOGranulate


class TestOOGranulate(cloudoooTestCase):

  def setUp(self):
    self.oogranulate = OOGranulate()

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
    self.assertRaises(NotImplementedError, self.oogranulate.getImageItemList,
                                           'file')

  def testGetImage(self):
    """Test if getImage() returns the right image file"""
    self.assertRaises(NotImplementedError, self.oogranulate.getImage,
                                     'file',
                                     'image_id',
                                     'format',
                                     'resolution')

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
