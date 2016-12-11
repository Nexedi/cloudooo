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
from cloudooo.handler.yformat.handler import Handler
from cloudooo.handler.ooo.handler import Handler as OOOHandler
from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite

OPENOFFICE = True

class TestHandler(HandlerTestCase):

  def afterSetUp(self):
    self.kw = dict(env=dict(PATH=self.env_path))

  def testConvertXLSXtoXLSYandBack(self):
    """Test conversion of xlsx to xlsy and back"""
    xlsx_orig_file = open("data/test.xlsx").read()
    xlsy_file = Handler(self.tmp_url, xlsx_orig_file, "xlsx", **self.kw).convert("xlsy")
    xlsx_file = Handler(self.tmp_url, xlsy_file, "xlsy", **self.kw).convert("xlsx")
    # magic not correctly determinate mime for xlsx files. i used ods, because it simple.
    ods_file = OOOHandler(self.tmp_url, xlsx_file, "xlsx", **self.kw).convert("ods")
    mime = magic.Magic(mime=True)
    ods_mimetype = mime.from_buffer(ods_file)
    self.assertEquals("application/vnd.oasis.opendocument.spreadsheet", ods_mimetype)

  def testgetMetadataFromImage(self):
    """Test getMetadata not implemented form yformats"""
    handler = Handler(self.tmp_url, "", "xlsy", **self.kw)
    self.assertRaises(NotImplementedError, handler.getMetadata)

  def testsetMetadata(self):
    """Test setMetadata not implemented for yformats"""
    handler = Handler(self.tmp_url, "", "xlsy", **self.kw)
    self.assertRaises(NotImplementedError, handler.setMetadata)


def test_suite():
  return make_suite(TestHandler)
