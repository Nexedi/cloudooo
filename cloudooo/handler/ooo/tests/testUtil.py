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
import logging
from cloudooo import util
from cloudooo.tests.handlerTestCase import make_suite
import mimetypes


class TestUtil(unittest.TestCase):
  """Test Utils"""

  def testLog(self):
    """Instanciate Log and test __call__ called function log"""
    util.configureLogger(logging.DEBUG)
    util.logger.info("Test Log")
    util.logger.debug("Test Log")
    util.configureLogger(logging.INFO)
    util.logger.info("Test Log")
    util.logger.debug("Test Log")

  def testConversion(self):
    """Test convertion to bool"""
    self.assertTrue(util.convertStringToBool('true'))
    self.assertEquals(util.convertStringToBool('false'), False)
    self.assertTrue(util.convertStringToBool('truE'))
    self.assertEquals(util.convertStringToBool('faLse'), False)
    self.assertEquals(util.convertStringToBool(''), None)

  def testLoadMimetypelist(self):
    """Test if the file with mimetypes is loaded correctly"""
    self.assertEquals(mimetypes.types_map.get(".ogv"), None)
    self.assertEquals(mimetypes.types_map.get(".3gp"), None)
    util.loadMimetypeList()
    self.assertEquals(mimetypes.types_map.get(".ogv"), "video/ogg")
    self.assertEquals(mimetypes.types_map.get(".3gp"), "video/3gpp")


def test_suite():
  return make_suite(TestUtil)

if "__main__" == __name__:
  suite = unittest.TestLoader().loadTestsFromTestCase(TestUtil)
  unittest.TextTestRunner(verbosity=2).run(suite)
