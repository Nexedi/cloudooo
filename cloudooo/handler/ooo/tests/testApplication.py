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
from cloudooo.handler.ooo.application.application import Application
from cloudoooTestCase import make_suite


class TestApplication(unittest.TestCase):

  def setUp(self):
    """Instantiate one application object and load settings on object"""
    self.application = Application()
    self.application.loadSettings('localhost', 9999, '/tmp/', '99')

  def testLoadSettings(self):
    """Test if settings are defined correctly"""
    self.assertEquals(self.application.hostname, 'localhost')
    self.assertEquals(self.application.port, 9999)
    self.assertEquals(self.application.path_run_dir, '/tmp/')
    self.assertEquals(self.application.display_id, '99')

  def testStartTimeout(self):
    """Test if the attribute timeout is defined correctly"""
    self.assertEquals(self.application.timeout, 20)
    application = Application()
    application.loadSettings('localhost', 9999, '/', '99', start_timeout=25)
    self.assertEquals(application.timeout, 25)

  def testgetAddress(self):
    """Test if getAddress() returns tuple with address correctly """
    self.assertEquals(self.application.getAddress(), ('localhost', 9999))

  def testPid(self):
    """As the application do not have the pid() should return None"""
    self.assertEquals(self.application.pid(), None)


def test_suite():
  return make_suite(TestApplication)

