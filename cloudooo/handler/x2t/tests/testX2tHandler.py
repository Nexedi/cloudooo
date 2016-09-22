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
from cloudooo.handler.x2t.handler import Handler
from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite

class TestHandler(HandlerTestCase):

  def afterSetUp(self):
    self.kw = dict(env=dict(PATH=self.env_path))

  def testConvertXlsx(self):
    """Test conversion of xlsx to xlsy and back"""
    y_data = Handler(self.tmp_url, open("data/test.xlsx").read(), "xlsx", **self.kw).convert("xlsy")
    self.assertTrue(y_data.startswith("XLSY;v2;5883;"), "%r... does not start with 'XLSY;v2;5883;'" % (y_data[:20],))

    x_data = Handler(self.tmp_url, y_data, "xlsy", **self.kw).convert("xlsx")
    # magic inspired by https://github.com/minad/mimemagic/pull/19/files
    self.assertIn("xl/", x_data[:2000])

  def testConvertXlsy(self):
    """Test conversion of xlsy to xlsx and back"""
    x_data = Handler(self.tmp_url, open("data/test.xlsy").read(), "xlsy", **self.kw).convert("xlsx")
    self.assertIn("xl/", x_data[:2000])

    y_data = Handler(self.tmp_url, x_data, "xlsx", **self.kw).convert("xlsy")
    self.assertTrue(y_data.startswith("XLSY;v2;10579;"), "%r... does not start with 'XLSY;v2;10579;'" % (y_data[:20],))

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
