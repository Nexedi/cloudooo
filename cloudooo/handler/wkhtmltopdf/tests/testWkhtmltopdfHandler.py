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

from base64 import b64encode

import magic
from cloudooo.handler.wkhtmltopdf.handler import Handler
from cloudooo.tests.handlerTestCase import HandlerTestCase


class TestHandler(HandlerTestCase):

  def afterSetUp(self):
    self.kw = dict(env=dict(PATH=self.env_path))

  def _testBase(self, html_path, **conversion_kw):
    with open(html_path, 'rb') as f:
      html_file = f.read()
    handler = Handler(self.tmp_url, html_file, "html", **self.kw)
    pdf_file = handler.convert("pdf", **conversion_kw)
    mime = magic.Magic(mime=True)
    pdf_mimetype = mime.from_buffer(pdf_file)
    self.assertEqual("application/pdf", pdf_mimetype)

  def testConvertHtmlWithPngDataUrlToPdf(self):
    """Test conversion of html with png data url to pdf"""
    self._testBase("data/test_with_png_dataurl.html")

  def testConvertHtmlWithScriptToPdf(self):
    """Test conversion of html with script to pdf"""
    self._testBase("data/test_with_script.html")

  def testConvertHtmlWithOpacityStyleToPdf(self):
    """Test conversion of html with opacity style to pdf

    Opacity style in a web pages causes Segmentation Fault only if wkhtmltopdf
    is not connected to a graphical service like Xorg.
    """
    self._testBase("data/test_with_opacity_style.html")

  # TODO: def testConvertHtmlWithHeaderAndFooter(self):

  def testConvertHtmlWithTableOfContent(self):
    """Test conversion of html with an additional table of content"""
    with open("data/test_toc.xsl", 'rb') as f:
      xsl_style_sheet_data = f.read()
    self._testBase(
      "data/test_with_toc.html",
      toc=True,
      xsl_style_sheet_data=b64encode(xsl_style_sheet_data),
    )
    # XXX how to check for table of content presence ?

  def testsetMetadata(self):
    """ Test if metadata are inserted correclty """
    handler = Handler(self.tmp_url, b"", "png", **self.kw)
    self.assertRaises(NotImplementedError, handler.setMetadata)

  def testGetAllowedConversionFormatList(self):
    """Test all combination of mimetype

    None of the types below define any mimetype parameter to not ignore so far.
    """
    get = Handler.getAllowedConversionFormatList
    # Handled mimetypes
    self.assertEqual(get("text/html;ignored=param"),
      [("application/pdf", "PDF - Portable Document Format")])

    # Unhandled mimetypes
    self.assertEqual(get("application/pdf;ignored=param"), [])

