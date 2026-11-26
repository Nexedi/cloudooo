# -*- coding: utf-8 -*-
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
##############################################################################

import unittest
from os import path
from cloudooo.grain import GranulateError
from cloudooo.handler.ooo.granulator import OOGranulator

DATA = path.join(path.dirname(__file__), 'data')


def getBlockList(name):
  with open(path.join(DATA, name), 'rb') as f:
    granulator = OOGranulator(f.read(), 'odt')
  try:
    return granulator.getBlockList()
  finally:
    granulator.trash()


class TestOooGranulatorBlockList(unittest.TestCase):
  """getBlockList only reads the ODF zip, LibreOffice is not needed."""

  def testHeadingsKeepOutlineLevel(self):
    block_list = getBlockList('granulate_chapters_test.odt')
    heading_list = [(b['level'], b['text']) for b in block_list
                    if b['type'] == 'heading']
    self.assertEqual(10, len(heading_list))
    self.assertEqual([(1, 'Title 1'), (2, 'Title 2'), (3, 'Title 3')],
                     heading_list[:3])
    self.assertEqual('Title 0', block_list[0]['text'])

  def testTables(self):
    block_list = getBlockList('granulate_table_test.odt')
    table_list = [b['text'] for b in block_list if b['type'] == 'table']
    self.assertEqual(3, len(table_list))
    first_row, second_row = table_list[0].split('\n')[:2]
    self.assertEqual('Name | Phone | Email', first_row)
    self.assertEqual('Hugo | +55 (22) 8888-8888 | hugomaia@tiolive.com',
                     second_row)
    # table text is not repeated as paragraphs
    self.assertFalse(any('hugomaia' in b['text'] for b in block_list
                         if b['type'] != 'table'))

  def testListItemsAndFrameText(self):
    block_list = getBlockList('granulate_test.odt')
    self.assertEqual(
      ['Introduction'],
      [b['text'] for b in block_list if b['type'] == 'list_item'][:1])
    self.assertEqual(3, sum(b['type'] == 'list_item' for b in block_list))

  def testNoEmptyBlockNorPages(self):
    for name in ('granulate_test.odt', 'granulate_table_test.odt', 'test.odt'):
      for block in getBlockList(name):
        self.assertTrue(block['text'].strip(), name)
        self.assertNotIn('page', block)

  def testNotAnOdfText(self):
    # a spreadsheet has no office:text body
    with self.assertRaises(GranulateError):
      with open(path.join(DATA, 'test.ods'), 'rb') as f:
        OOGranulator(f.read(), 'ods').getBlockList()


if __name__ == '__main__':
  unittest.main()
