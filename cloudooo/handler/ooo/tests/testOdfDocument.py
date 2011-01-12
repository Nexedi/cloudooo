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

from zipfile import ZipFile
from lxml import etree
from cloudoooTestCase import CloudoooTestCase, make_suite
from cloudooo.handler.ooo.document import OdfDocument

class TestOdfDocument(CloudoooTestCase):

  def setUp(self):
    data = open('./data/granulate_test.odt').read()
    self.oodocument = OdfDocument(data, 'odt')

  def testReceivedGoodFile(self):
    """Test if received path is from a good document returing an ZipFile"""
    self.assertTrue(isinstance(self.oodocument._zipfile, ZipFile))

  def testGetContentXml(self):
    """Test if the getContentXml method returns the content.xml file"""
    content_xml = self.oodocument.getContentXml()
    self.assertTrue('The content of this file is just' in content_xml)

  def testGetExistentFile(self):
    """Test if the getFile method returns the requested file"""
    requested_file = self.oodocument.getFile('content.xml')
    self.assertEquals(requested_file, self.oodocument.getContentXml())

  def testGetNotPresentFile(self):
    """Test if the getFile method returns None for not present file request"""
    requested_file = self.oodocument.getFile('not_present.xml')
    self.assertEquals(requested_file, '')

  def testParseContent(self):
    """Test if the _parsed_content attribute is the parsed content.xml"""
    # XXX not sure it is good to store parsed document everytime
    self.assertTrue(isinstance(self.oodocument.parsed_content, etree._Element))
    self.assertTrue(self.oodocument.parsed_content.tag.endswith(
                    'document-content'))


def test_suite():
  return make_suite(TestOdfDocument)

