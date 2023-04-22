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
from lxml import etree
from cloudooo.tests.handlerTestCase import HandlerTestCase
from cloudooo.handler.ooo.document import OdfDocument


class TestOdfDocument(HandlerTestCase):

  def setUp(self):
    with open('./data/granulate_test.odt', 'rb') as f:
      data = f.read()
    self.oodocument = OdfDocument(data, 'odt')

  def testReceivedGoodFile(self):
    """Test if received path is from a good document returing an ZipFile"""
    self.assertIsInstance(self.oodocument._zipfile, ZipFile)

  def testGetContentXml(self):
    """Test if the getContentXml method returns the content.xml file"""
    content_xml = self.oodocument.getContentXml()
    self.assertIn(b'The content of this file is just', content_xml)

  def testGetExistentFile(self):
    """Test if the getFile method returns the requested file"""
    requested_file = self.oodocument.getFile('content.xml')
    self.assertEqual(requested_file, self.oodocument.getContentXml())

  def testGetNotPresentFile(self):
    """Test if the getFile method returns None for not present file request"""
    requested_file = self.oodocument.getFile('not_present.xml')
    self.assertEqual(requested_file, '')

  def testParseContent(self):
    """Test if the _parsed_content attribute is the parsed content.xml"""
    # XXX not sure it is good to store parsed document everytime
    self.assertIsInstance(self.oodocument.parsed_content, etree._Element)
    self.assertTrue(self.oodocument.parsed_content.tag.endswith(
                    'document-content'))


