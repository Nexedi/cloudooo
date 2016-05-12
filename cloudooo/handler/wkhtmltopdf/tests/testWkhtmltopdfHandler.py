##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
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
from cloudooo.handler.wkhtmltopdf.handler import Handler
from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite


class TestHandler(HandlerTestCase):

  def afterSetUp(self):
    self.kw = dict(env=dict(PATH=self.env_path))

  def testConvertHtmlWithPngDataUrlToPdf(self):
    """Test conversion of html with png data url to pdf"""
    html_file = open("data/test_with_png_dataurl.html").read()
    handler = Handler(self.tmp_url, html_file, "html", **self.kw)
    pdf_file = handler.convert("pdf")
    mime = magic.Magic(mime=True)
    pdf_mimetype = mime.from_buffer(pdf_file)
    self.assertEquals("application/pdf", pdf_mimetype)

  def testConvertHtmlWithScriptToPdf(self):
    """Test conversion of html with script to pdf"""
    html_file = open("data/test_with_script.html").read()
    handler = Handler(self.tmp_url, html_file, "html", **self.kw)
    pdf_file = handler.convert("pdf")
    mime = magic.Magic(mime=True)
    pdf_mimetype = mime.from_buffer(pdf_file)
    self.assertEquals("application/pdf", pdf_mimetype)

  # TODO: def testConvertHtmlWithHeaderAndFooter(self):

  def testsetMetadata(self):
    """ Test if metadata are inserted correclty """
    handler = Handler(self.tmp_url, "", "png", **self.kw)
    self.assertRaises(NotImplementedError, handler.setMetadata)


def test_suite():
  return make_suite(TestHandler)
