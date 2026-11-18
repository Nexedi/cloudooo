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
import tempfile
from base64 import encodebytes
from unittest.mock import patch
from os import path
from cloudooo.grain import GranulateError
from cloudooo.manager import Manager

OOO_DATA = path.join(path.dirname(__file__), '..', 'handler', 'ooo', 'tests',
                     'data')
PDF_DATA = path.join(path.dirname(__file__), '..', 'handler', 'pdf', 'tests',
                     'data')

HTML_DOCUMENT = b"""<!DOCTYPE html>
<html><head><title>Not readable</title></head><body>
<h1>Introduction</h1><p>Hello <b>world</b>.</p>
<h2>Details</h2><p>More text.</p>
<table><tr><th>Name</th><th>Value</th></tr><tr><td>One</td><td>Two</td></tr></table>
<script>hiddenText()</script>
</body></html>"""


def b64(directory, name):
  with open(path.join(directory, name), 'rb') as f:
    return encodebytes(f.read()).decode()


def b64html():
  return encodebytes(HTML_DOCUMENT).decode()


class TestGranulateFile(unittest.TestCase):
  """PDF and ODT are read directly, except when a page range is requested."""

  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.addCleanup(self.directory.cleanup)
    self.manager = Manager(self.directory.name, mimetype_registry=[],
                           handler_dict={})

  def testPdf(self):
    grain_list = self.manager.granulateFile(b64(PDF_DATA, 'test.pdf'), 'pdf')
    self.assertEqual(6, len(grain_list))
    self.assertEqual(['Front', 'Diapo 2'],
                     [g['context'] for g in grain_list[:2]])
    self.assertEqual((1, 1), (grain_list[0]['page_start'],
                              grain_list[0]['page_end']))

  def testMimetypeAsSourceFormat(self):
    self.assertEqual(
      self.manager.granulateFile(b64(PDF_DATA, 'test.pdf'), 'pdf'),
      self.manager.granulateFile(b64(PDF_DATA, 'test.pdf'), 'application/pdf'))

  def testPdfPageRangeKeepsSectionContext(self):
    grain_list = self.manager.granulateFile(
      b64(PDF_DATA, 'test.pdf'), 'pdf',
      {'page_range': [4, 5], 'strategy': 'page'})
    self.assertEqual([4, 5], [g['page_start'] for g in grain_list])
    self.assertEqual(['Diapo 4', 'Diapo 5'], [g['context'] for g in grain_list])

  def testPdfSizeLimit(self):
    grain_list = self.manager.granulateFile(
      b64(PDF_DATA, 'test.pdf'), 'pdf', {'max_chars': 150, 'overlap_chars': 20})
    self.assertGreater(len(grain_list), 6)
    self.assertTrue(all(g['char_count'] <= 150 for g in grain_list))

  def testOdt(self):
    grain_list = self.manager.granulateFile(
      b64(OOO_DATA, 'granulate_chapters_test.odt'), 'odt')
    self.assertEqual('Title 1 > Title 2', grain_list[2]['context'])
    self.assertNotIn('page_start', grain_list[0])

  def testOdtPageRange(self):
    odt = b64(OOO_DATA, 'granulate_chapters_test.odt')
    pdf = b64(PDF_DATA, 'test.pdf')
    with patch.object(self.manager, 'convertFile', return_value=pdf) as convert:
      grain_list = self.manager.granulateFile(
        odt, 'odt', {'page_range': [4, 5], 'strategy': 'page'})
    convert.assert_called_once_with(odt, 'odt', 'pdf', zip=False)
    self.assertEqual([4, 5], [g['page_start'] for g in grain_list])
    self.assertEqual(['Diapo 4', 'Diapo 5'], [g['context'] for g in grain_list])
    with patch.object(self.manager, 'convertFile', return_value=pdf):
      with self.assertRaises(GranulateError):
        self.manager.granulateFile(odt, 'odt', {'page_range': [9, 10]})

  def testHtml(self):
    grain_list = self.manager.granulateFile(b64html(), 'html')
    self.assertEqual(3, len(grain_list))
    self.assertEqual(['Introduction', 'Introduction > Details',
                      'Introduction > Details'],
                     [g['context'] for g in grain_list])
    self.assertEqual('table', grain_list[2]['type'])
    self.assertEqual('Name | Value\nOne | Two', grain_list[2]['text'])
    self.assertTrue(all('page_start' not in g for g in grain_list))
    self.assertNotIn('hiddenText', str(grain_list))

  def testHtmlSourceFormats(self):
    expected = self.manager.granulateFile(b64html(), 'html')
    for source_format in ('htm', 'xhtml', 'text/html',
                          'application/xhtml+xml'):
      self.assertEqual(
        expected, self.manager.granulateFile(b64html(), source_format))

  def testHtmlTablesCanBeExcluded(self):
    grain_list = self.manager.granulateFile(
      b64html(), 'html', {'include_tables': False})
    self.assertEqual(2, len(grain_list))
    self.assertTrue(all(g['type'] == 'text' for g in grain_list))

  def testOdtTables(self):
    document = b64(OOO_DATA, 'granulate_table_test.odt')
    grain_list = self.manager.granulateFile(document, 'odt')
    self.assertEqual(3, sum(g['type'] == 'table' for g in grain_list))
    grain_list = self.manager.granulateFile(
      document, 'odt', {'include_tables': False})
    self.assertEqual(0, sum(g['type'] == 'table' for g in grain_list))

  def testResultIsXmlRpcMarshallable(self):
    from xmlrpc.client import dumps
    for name, directory, fmt in (('test.pdf', PDF_DATA, 'pdf'),
                                 ('granulate_test.odt', OOO_DATA, 'odt')):
      grain_list = self.manager.granulateFile(b64(directory, name), fmt)
      dumps((grain_list,), allow_none=False)
    dumps((self.manager.granulateFile(b64html(), 'html'),),
          allow_none=False)

  def testErrors(self):
    pdf = b64(PDF_DATA, 'test.pdf')
    for args in ((pdf, 'pdf', {'strategy': 'unknown'}),
                 (pdf, 'pdf', {'page_range': [9, 10]}),
                 (b64html(), 'html', {'page_range': [1, 2]}),
                 (encodebytes(b'not a pdf').decode(), 'pdf', {}),
                 (pdf, 'foo/bar-unknown', {})):
      with self.assertRaises(GranulateError, msg=args[1:]):
        self.manager.granulateFile(*args)


if __name__ == '__main__':
  unittest.main()
