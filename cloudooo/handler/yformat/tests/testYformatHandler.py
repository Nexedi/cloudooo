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
from cloudooo.handler.imagemagick.handler import Handler
from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite


class TestHandler(HandlerTestCase):

  def afterSetUp(self):
    self.kw = dict(env=dict(PATH=self.env_path))

  def testConvertXLSXtoXLSYandBack(self):
    """Test conversion of png to jpg"""
    xlsx_orig_file = open("data/test.xlsx").read()
    xlsy_file = Handler(self.tmp_url, xlsx_orig_file, "xlsx", **self.kw).convert("xlsy")
    xlsx_file = Handler(self.tmp_url, xlsy_file, "xlsy", **self.kw).convert("xlsx")
    mime = magic.Magic(mime=True)
    xlsx_mimetype = mime.from_buffer(xlsx_file)
    self.assertEquals("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", xlsx_mimetype)

  def testgetMetadataFromImage(self):
    """Test if metadata is extracted from image correctly"""
    handler = Handler(self.tmp_url, "", "xlsx", **self.kw)
    self.assertRaises(NotImplementedError, handler.getMetadata)

  def testsetMetadata(self):
    """ Test if metadata are inserted correclty """
    handler = Handler(self.tmp_url, "", "xlsx", **self.kw)
    self.assertRaises(NotImplementedError, handler.setMetadata)


def test_suite():
  return make_suite(TestHandler)
