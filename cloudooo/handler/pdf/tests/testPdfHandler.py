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


from cloudooo.handler.pdf.handler import Handler
from cloudooo.tests.handlerTestCase import HandlerTestCase


class TestHandler(HandlerTestCase):

  def afterSetUp(self):
    self.kw = dict(env=dict(PATH=self.env_path))

  def testConvertPDFtoText(self):
    """Test conversion of pdf to txt"""
    with open("data/test.pdf", "rb") as f:
      pdf_document = f.read()
    handler = Handler(self.tmp_url, pdf_document, "pdf", **self.kw)
    txt_document = handler.convert("txt")
    self.assertTrue(txt_document.startswith(b"UNG Docs Architecture"))

  def testgetMetadata(self):
    """Test if the metadata are extracted correctly"""
    with open("data/test.pdf", "rb") as f:
      pdf_document = f.read()
    handler = Handler(self.tmp_url, pdf_document, "pdf", **self.kw)
    metadata = handler.getMetadata()
    self.assertIsInstance(metadata, dict)
    self.assertNotEqual(metadata, {})
    self.assertEqual(metadata["title"], 'Free Cloud Alliance Presentation')

  def testsetMetadata(self):
    """Test if the metadata is inserted correctly"""
    with open("data/test.pdf", "rb") as f:
      pdf_document = f.read()
    handler = Handler(self.tmp_url, pdf_document, "pdf", **self.kw)
    metadata_dict = {"title": "Set Metadata Test", "creator": "gabriel\'@"}
    new_document = handler.setMetadata(metadata_dict)
    handler = Handler(self.tmp_url, new_document, "pdf", **self.kw)
    metadata = handler.getMetadata()
    self.assertEqual(metadata["title"], 'Set Metadata Test')
    self.assertEqual(metadata['creator'], 'gabriel\'@')

  def testGetAllowedConversionFormatList(self):
    """Test all combination of mimetype

    None of the types below define any mimetype parameter to not ignore so far.
    """
    get = Handler.getAllowedConversionFormatList
    # Handled mimetypes
    self.assertEqual(get("application/pdf;ignored=param"),
      [("text/plain", "Plain Text")])

    # Unhandled mimetypes
    self.assertEqual(get("text/plain;ignored=param"), [])
    self.assertEqual(get("text/plain;charset=UTF-8;ignored=param"), [])

