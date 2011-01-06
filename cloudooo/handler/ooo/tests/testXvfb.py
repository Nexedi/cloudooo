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
from cloudoooTestCase import CloudoooTestCase, make_suite
from cloudooo.handler.ooo.application.xvfb import Xvfb
from cloudooo.handler.ooo.utils.utils import waitStopDaemon


class TestXvfb(CloudoooTestCase):

  def afterSetUp(self):
    """Instanciate a xvfb object"""
    self.xvfb = Xvfb()
    self.xvfb.loadSettings(self.hostname,
                          int(self.virtual_display_port_int),
                          self.working_path,
                          self.virtual_display_id,
                          virtual_screen='1')

  def testPid(self):
    """Test pid function to validate if the return is correctly"""
    self.assertEquals(self.xvfb.pid(), None)
    self.xvfb.start()
    self.assertNotEquals(self.xvfb.pid(), None)
    self.assertTrue(self.xvfb.status())
    self.xvfb.stop()
    self.assertNotEquals(self.xvfb.pid(), None)
    self.assertEquals(self.xvfb.status(), False)

  def testStatus(self):
    """Test if xvfb is started and stopped correctly"""
    self.assertFalse(self.xvfb.status())
    try:
      self.xvfb.start()
      self.assertTrue(self.xvfb.status())
    finally:
      self.xvfb.stop()
      waitStopDaemon(self.xvfb)
    self.assertFalse(self.xvfb.status())


def test_suite():
  return make_suite(TestXvfb)

if "__main__" == __name__:
  import sys
  from cloudoooTestCase import loadConfig
  loadConfig(sys.argv[1])
  suite = unittest.TestLoader().loadTestsFromTestCase(TestXvfb)
  unittest.TextTestRunner(verbosity=2).run(suite)
