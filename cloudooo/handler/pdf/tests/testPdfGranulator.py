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
from io import BytesIO
from os import path
from pypdf import PdfReader, PdfWriter
from cloudooo.grain import GranulateError
from cloudooo.handler.pdf.granulator import PdfGranulator, _joinLineList

# 6 pages, one bookmark per page: Front, Diapo 2, ... Diapo 6
PDF_PATH = path.join(path.dirname(__file__), 'data', 'test.pdf')


def getPdf():
  with open(PDF_PATH, 'rb') as f:
    return f.read()


class TestPdfGranulator(unittest.TestCase):

  def setUp(self):
    self.granulator = PdfGranulator(getPdf())

  def testPageCount(self):
    self.assertEqual(6, self.granulator.getPageCount())

  def testBlockListHasPagesAndOutlineHeadings(self):
    block_list = self.granulator.getBlockList()
    self.assertEqual({1, 2, 3, 4, 5, 6}, {b['page'] for b in block_list})
    heading_list = [(b['level'], b['text'], b['page'])
                    for b in block_list if b['type'] == 'heading']
    self.assertEqual(
      [(1, 'Front', 1), (1, 'Diapo 2', 2), (1, 'Diapo 3', 3)],
      heading_list[:3])
    # the heading is the first block of its page, and is not repeated
    for page in range(1, 7):
      page_list = [b for b in block_list if b['page'] == page]
      self.assertEqual('heading', page_list[0]['type'])
      self.assertEqual(1, sum(b['type'] == 'heading' for b in page_list))
    self.assertTrue(any('Word Processor' in b['text'] for b in block_list
                        if b['page'] == 2))

  def testPageRange(self):
    block_list = self.granulator.getBlockList(2, 3)
    self.assertEqual({2, 3}, {b['page'] for b in block_list})
    self.assertEqual({6}, {b['page'] for b in
                           self.granulator.getBlockList(6, 100)})

  def testPageRangeAfterLastPage(self):
    with self.assertRaises(GranulateError):
      self.granulator.getBlockList(7, 8)

  def testOutlineContext(self):
    self.assertEqual([], self.granulator.getOutlineContext(1))
    self.assertEqual([(1, 'Front'), (1, 'Diapo 2')],
                     self.granulator.getOutlineContext(3))

  def testInvalidPdf(self):
    with self.assertRaises(GranulateError):
      PdfGranulator(b'this is not a pdf')

  def testEncryptedPdf(self):
    writer = PdfWriter(clone_from=PdfReader(BytesIO(getPdf())))
    writer.encrypt('secret', algorithm='RC4-128')
    output = BytesIO()
    writer.write(output)
    with self.assertRaises(GranulateError):
      PdfGranulator(output.getvalue())

  def testJoinLineList(self):
    self.assertEqual('hello world', _joinLineList(['hello', 'world']))
    self.assertEqual('information', _joinLineList(['infor-', 'mation']))
    self.assertEqual('state-of- The', _joinLineList(['state-of-', 'The']))


if __name__ == '__main__':
  unittest.main()
