##############################################################################
#
# Copyright (c) 2009-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Gabriel M. Monnerat <gabriel@tiolive.com>
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


import magic
import os.path
from zipfile import ZipFile
from cStringIO import StringIO
from cloudooo.handler.x2t.handler import Handler
from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite

class TestHandler(HandlerTestCase):

  def afterSetUp(self):
    self.kw = dict(env=dict(PATH=self.env_path))

  def testConvertXlsx(self):
    """Test conversion of xlsx to xlsy and back"""
    y_data = Handler(self.tmp_url, open("data/test.xlsx").read(), "xlsx", **self.kw).convert("xlsy")
    y_body_data = ZipFile(StringIO(y_data)).open("body.txt").read()
    self.assertTrue(y_body_data.startswith("XLSY;v2;5883;"), "%r... does not start with 'XLSY;v2;5883;'" % (y_body_data[:20],))

    x_data = Handler(self.tmp_url, y_data, "xlsy", **self.kw).convert("xlsx")
    # magic inspired by https://github.com/minad/mimemagic/pull/19/files
    self.assertIn("xl/", x_data[:2000])

  def testConvertXlsy(self):
    """Test conversion of xlsy to xlsx and back"""
    x_data = Handler(self.tmp_url, open("data/test_body.xlsy").read(), "xlsy", **self.kw).convert("xlsx")
    self.assertIn("xl/", x_data[:2000])
    x_data = Handler(self.tmp_url, open("data/test.xlsy").read(), "xlsy", **self.kw).convert("xlsx")
    self.assertIn("xl/", x_data[:2000])

    y_data = Handler(self.tmp_url, x_data, "xlsx", **self.kw).convert("xlsy")
    y_body_data = ZipFile(StringIO(y_data)).open("body.txt").read()
    self.assertTrue(y_body_data.startswith("XLSY;v2;10579;"), "%r... does not start with 'XLSY;v2;10579;'" % (y_body_data[:20],))

  def testConvertDocx(self):
    """Test conversion of docx to docy and back"""
    y_data = Handler(self.tmp_url, open("data/test_with_image.docx").read(), "docx", **self.kw).convert("docy")
    y_zip = ZipFile(StringIO(y_data))
    y_body_data = y_zip.open("body.txt").read()
    self.assertTrue(y_body_data.startswith("DOCY;v5;2795;"), "%r... does not start with 'DOCY;v5;2795;'" % (y_body_data[:20],))
    y_zip.open("media/image1.png")

    x_data = Handler(self.tmp_url, y_data, "docy", **self.kw).convert("docx")
    # magic inspired by https://github.com/minad/mimemagic/pull/19/files
    self.assertIn("word/", x_data[:2000])

  def testConvertDocy(self):
    """Test conversion of docy to docx and back"""
    x_data = Handler(self.tmp_url, open("data/test_with_image.docy").read(), "docy", **self.kw).convert("docx")
    self.assertIn("word/", x_data[:2000])

    y_data = Handler(self.tmp_url, x_data, "docx", **self.kw).convert("docy")
    y_zip = ZipFile(StringIO(y_data))
    y_body_data = y_zip.open("body.txt").read()
    self.assertTrue(y_body_data.startswith("DOCY;v5;7519;"), "%r... does not start with 'DOCY;v5;7519;'" % (y_body_data[:20],))
    y_zip.open("media/image1.png")

  def testgetMetadata(self):
    """Test getMetadata from yformats (not implemented)"""
    handler = Handler(self.tmp_url, "", "xlsy", **self.kw)
    #   Of course, expected behavior should be a dict of internal metadata
    # but don't know how to handle it so far.
    self.assertEquals(handler.getMetadata(), {})

  def testsetMetadata(self):
    """Test setMetadata for yformats (not implemented)"""
    handler = Handler(self.tmp_url, "", "xlsy", **self.kw)
    #   Of course, expected behavior should be an updated data with new
    # internal metadata but don't know how to handle it so far.
    self.assertEquals(handler.setMetadata(), "")

  def testGetAllowedConversionFormatList(self):
    """Test all combination of mimetype

    None of the types below define any mimetype parameter to not ignore so far.
    """
    get = Handler.getAllowedConversionFormatList
    self.assertEquals(get("application/x-asc-text;ignored=param"),
      [("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "Word 2007 Document"),
       ('application/vnd.oasis.opendocument.text', 'ODF Text Document')])
    self.assertEquals(get("application/x-asc-spreadsheet;ignored=param"),
      [("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Excel 2007 Spreadsheet"),
	('application/vnd.oasis.opendocument.spreadsheet', 'ODF Spreadsheet Document')])
    self.assertEquals(get("application/x-asc-presentation;ignored=param"),
      [("application/vnd.openxmlformats-officedocument.presentationml.presentation", "PowerPoint 2007 Presentation"),
	('application/vnd.oasis.opendocument.presentation', 'ODF Presentation Document')])

def test_suite():
  return make_suite(TestHandler)
