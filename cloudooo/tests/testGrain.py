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
from hashlib import sha256
from cloudooo.grain import (
  GranulateError, parseGranulateKw, granulateBlockList)


def heading(text, level=1, **kw):
  return dict(type='heading', text=text, level=level, **kw)


def paragraph(text, **kw):
  return dict(type='paragraph', text=text, **kw)


SENTENCE = 'This is sentence number %03d of the test document.'


def longText(count):
  return ' '.join(SENTENCE % i for i in range(count))


class TestParseGranulateKw(unittest.TestCase):

  def testDefaults(self):
    options = parseGranulateKw({})
    self.assertEqual('structure', options['strategy'])
    self.assertEqual(1500, options['max_chars'])
    self.assertEqual(200, options['overlap_chars'])
    self.assertTrue(options['include_tables'])
    self.assertIsNone(options['page_range'])

  def testInvalid(self):
    for kw in ({'unknown': 1}, {'strategy': 'foo'}, {'max_chars': 10},
               {'max_chars': '1500'}, {'max_chars': 1000, 'overlap_chars': 600},
               {'overlap_chars': -1}, {'page_range': [0, 3]},
               {'page_range': [4, 3]}, {'page_range': 3}):
      with self.assertRaises(GranulateError, msg=kw):
        parseGranulateKw(kw)

  def testPageRange(self):
    self.assertEqual((2, 5), parseGranulateKw({'page_range': [2, 5]})['page_range'])


class TestGranulateBlockList(unittest.TestCase):

  def testHeadingsStartNewGrainWithContext(self):
    grain_list = granulateBlockList([
      heading('Chapter 1'), paragraph('one'),
      heading('Section 1.1', 2), paragraph('two'),
      heading('Chapter 2'), paragraph('three'),
    ])
    self.assertEqual(
      [('Chapter 1', 'Chapter 1\n\none'),
       ('Chapter 1 > Section 1.1', 'Section 1.1\n\ntwo'),
       ('Chapter 2', 'Chapter 2\n\nthree')],
      [(g['context'], g['text']) for g in grain_list])
    self.assertEqual([0, 1, 2], [g['index'] for g in grain_list])

  def testSmallParagraphsAreMerged(self):
    grain_list = granulateBlockList(
      [heading('T')] + [paragraph('p%d' % i) for i in range(5)])
    self.assertEqual(1, len(grain_list))
    self.assertEqual([0, 1, 2, 3, 4, 5], grain_list[0]['block_ids'])

  def testMaxCharsAndOverlap(self):
    block_list = [heading('Title'), paragraph(longText(60))]
    grain_list = granulateBlockList(
      block_list, max_chars=400, overlap_chars=80)
    self.assertGreater(len(grain_list), 5)
    for grain in grain_list:
      self.assertLessEqual(grain['char_count'], 400)
      self.assertEqual('Title', grain['context'])
    # consecutive grains share text
    for previous, grain in zip(grain_list, grain_list[1:]):
      first_words = grain['text'].split('\n')[0]
      self.assertTrue(first_words and first_words in previous['text'],
                      (first_words, previous['text']))
    # nothing is lost
    text = '\n'.join(g['text'] for g in grain_list)
    for i in range(60):
      self.assertIn(SENTENCE % i, text)

  def testNoOverlapWhenDisabled(self):
    grain_list = granulateBlockList(
      [paragraph(longText(30))], max_chars=300, overlap_chars=0)
    joined = ' '.join(g['text'] for g in grain_list)
    self.assertEqual(longText(30), joined)

  def testNoOverlapAcrossHeadings(self):
    grain_list = granulateBlockList(
      [heading('A'), paragraph(longText(20)), heading('B'), paragraph('x')],
      max_chars=300, overlap_chars=60)
    self.assertEqual('B\n\nx', grain_list[-1]['text'])

  def testWordLongerThanMaxChars(self):
    grain_list = granulateBlockList([paragraph('x' * 1000)], max_chars=300,
                                    overlap_chars=0)
    self.assertTrue(all(g['char_count'] <= 300 for g in grain_list))
    self.assertEqual('x' * 1000, ''.join(g['text'] for g in grain_list))

  def testTable(self):
    table = dict(type='table', text='Name | Age\nAda | 36\nBob | 41')
    grain_list = granulateBlockList(
      [heading('T'), paragraph('intro'), table, paragraph('after')])
    self.assertEqual(['text', 'table', 'text'], [g['type'] for g in grain_list])
    self.assertEqual(table['text'], grain_list[1]['text'])
    self.assertEqual('T', grain_list[1]['context'])
    grain, = granulateBlockList(
      [heading('T'), paragraph('intro'), table, paragraph('after')],
      include_tables=False)
    self.assertEqual('T\n\nintro\n\nafter', grain['text'])

  def testLargeTableIsSplitByRowsWithHeader(self):
    rows = ['Key | Value'] + ['row%03d | %s' % (i, 'v' * 20) for i in range(40)]
    grain_list = granulateBlockList(
      [dict(type='table', text='\n'.join(rows))], max_chars=300)
    self.assertGreater(len(grain_list), 2)
    for grain in grain_list:
      self.assertEqual('table', grain['type'])
      self.assertLessEqual(grain['char_count'], 300)
      self.assertEqual('Key | Value', grain['text'].split('\n')[0])
    body = [line for g in grain_list for line in g['text'].split('\n')[1:]]
    self.assertEqual(rows[1:], body)

  def testPageStrategy(self):
    block_list = [paragraph('a', page=1), paragraph('b', page=1),
                  heading('H', page=2), paragraph('c', page=2),
                  paragraph('d', page=3)]
    grain_list = granulateBlockList(block_list, strategy='page')
    self.assertEqual(['a\n\nb', 'H\n\nc', 'd'], [g['text'] for g in grain_list])
    self.assertEqual([(1, 1), (2, 2), (3, 3)],
                     [(g['page_start'], g['page_end']) for g in grain_list])

  def testStructureStrategyKeepsPages(self):
    block_list = [heading('H', page=1), paragraph('a', page=1),
                  paragraph('b', page=2)]
    grain, = granulateBlockList(block_list)
    self.assertEqual((1, 2), (grain['page_start'], grain['page_end']))

  def testNoPageKeysWithoutPages(self):
    grain, = granulateBlockList([paragraph('a')])
    self.assertNotIn('page_start', grain)
    self.assertNotIn('page_end', grain)

  def testFixedStrategyIgnoresStructure(self):
    grain_list = granulateBlockList(
      [heading('A'), paragraph('one'), heading('B'), paragraph('two')],
      strategy='fixed')
    self.assertEqual(['A\n\none\n\nB\n\ntwo'], [g['text'] for g in grain_list])

  def testBlocksStrategy(self):
    block_list = granulateBlockList(
      [heading('A'), paragraph('x'), heading('B', 2), paragraph('y')],
      strategy='blocks')
    self.assertEqual([0, 1, 2, 3], [b['id'] for b in block_list])
    self.assertEqual([['A'], ['A'], ['A', 'B'], ['A', 'B']],
                     [b['section_path'] for b in block_list])

  def testInitialHeadingList(self):
    grain, = granulateBlockList(
      [paragraph('x')], initial_heading_list=[(1, 'Part'), (2, 'Chapter')])
    self.assertEqual('Part > Chapter', grain['context'])

  def testContentHash(self):
    grain, = granulateBlockList([paragraph(u'héllo')])
    self.assertEqual(sha256(u'héllo'.encode('utf-8')).hexdigest(),
                     grain['content_hash'])

  def testEmpty(self):
    self.assertEqual([], granulateBlockList([]))


if __name__ == '__main__':
  unittest.main()
