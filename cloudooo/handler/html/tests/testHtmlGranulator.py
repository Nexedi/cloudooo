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

from cloudooo.grain import GranulateError, granulateBlockList
from cloudooo.handler.html.granulator import HtmlGranulator


DOCUMENT = b"""<!DOCTYPE html>
<html><head><title>Not readable</title><style>p {}</style></head><body>
<h1>Introduction</h1>
<p>Hello <strong>world</strong>.</p>
<h2>Details</h2>
<p>First detail.</p>
<ul>
  <li>Alpha</li>
  <li>Beta<ul><li>Gamma</li></ul></li>
</ul>
<table><thead><tr><th>Name</th><th>Value</th></tr></thead>
<tbody><tr><td>One</td><td>1</td></tr></tbody></table>
<script>doNotExtractThis()</script>
<p>After table.</p>
</body></html>"""


class TestHtmlGranulator(unittest.TestCase):

  def testBlockList(self):
    self.assertEqual([
      {'type': 'heading', 'text': 'Introduction', 'level': 1},
      {'type': 'paragraph', 'text': 'Hello world.'},
      {'type': 'heading', 'text': 'Details', 'level': 2},
      {'type': 'paragraph', 'text': 'First detail.'},
      {'type': 'list_item', 'text': 'Alpha'},
      {'type': 'list_item', 'text': 'Beta'},
      {'type': 'list_item', 'text': 'Gamma'},
      {'type': 'table', 'text': 'Name | Value\nOne | 1'},
      {'type': 'paragraph', 'text': 'After table.'},
    ], HtmlGranulator(DOCUMENT).getBlockList())

  def testGrainContextAndTable(self):
    grain_list = granulateBlockList(HtmlGranulator(DOCUMENT).getBlockList())
    self.assertEqual(['Introduction',
                      'Introduction > Details',
                      'Introduction > Details',
                      'Introduction > Details'],
                     [grain['context'] for grain in grain_list])
    self.assertEqual('table', grain_list[2]['type'])
    self.assertNotIn('page_start', grain_list[0])
    self.assertEqual('Introduction\n\nHello world.', grain_list[0]['text'])
    self.assertNotIn('doNotExtractThis', str(grain_list))

  def testIncludeTables(self):
    block_list = HtmlGranulator(DOCUMENT).getBlockList()
    grain_list = granulateBlockList(block_list, include_tables=False)
    self.assertEqual(2, len(grain_list))
    self.assertTrue(all(grain['type'] == 'text' for grain in grain_list))

  def testFragmentAndLooseText(self):
    block_list = HtmlGranulator(
      b'<div>Loose text <span>continued</span><p>Paragraph</p>tail</div>'
    ).getBlockList()
    self.assertEqual([
      {'type': 'paragraph', 'text': 'Loose text continued'},
      {'type': 'paragraph', 'text': 'Paragraph'},
      {'type': 'paragraph', 'text': 'tail'},
    ], block_list)

  def testLineBreaksAndEntities(self):
    block_list = HtmlGranulator(
      b'<p>First&nbsp;line<br>Second &amp; last</p>').getBlockList()
    self.assertEqual('First line\nSecond & last',
                     block_list[0]['text'])

  def testEmptyDocument(self):
    with self.assertRaises(GranulateError):
      HtmlGranulator(b'').getBlockList()


if __name__ == '__main__':
  unittest.main()
