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


import unittest
from cloudooo.handler.pdf.handler import PDFHandler
from cloudooo.handler.tests.handlerTestCase import HandlerTestCase
from types import DictType


class TestPDFHandler(HandlerTestCase):

  def testConvertPDFtoText(self):
    """Test conversion of pdf to txt"""
    pdf_document = open("data/test.pdf").read()
    handler = PDFHandler(self.tmp_url, pdf_document, "pdf")
    txt_document = handler.convert("txt")
    self.assertTrue(txt_document.startswith("UNG Docs Architecture"))

  def testgetMetadata(self):
    """Test if the metadata are extracted correctly"""
    pdf_document = open("data/test.pdf").read()
    kw = dict(env=dict(PATH="/hd/cloudooo_handler_ooo/software/parts/xpdf/bin"))
    handler = PDFHandler(self.tmp_url, pdf_document, "pdf", **kw)
    metadata = handler.getMetadata()
    self.assertEquals(type(metadata), DictType)
    self.assertNotEquals(metadata, {})
    self.assertEquals(metadata["title"], 'Free Cloud Alliance Presentation')


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPDFHandler))
  return suite
