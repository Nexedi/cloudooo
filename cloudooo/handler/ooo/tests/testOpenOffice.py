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

from cloudoooTestCase import CloudoooTestCase
from cloudooo.handler.ooo.application.openoffice import OpenOffice
from cloudoooTestCase import make_suite
from cloudooo.handler.ooo.utils.utils import waitStopDaemon

OPENOFFICE = True

class TestOpenOffice(CloudoooTestCase):
  """Test OpenOffice object and manipulation of OOo Instance"""

  def afterSetUp(self):
    """Instantiate one OpenOffice"""
    self.openoffice = OpenOffice()
    self.openoffice.loadSettings("localhost", 4090,
                                self.working_path,
                                self.office_binary_path,
                                self.uno_path,
                                'en')
    self.openoffice.start()

  def tearDown(self):
    """Stop the OpenOffice"""
    if self.openoffice.status():
      self.openoffice.stop()

  def testPid(self):
    """Test pid function to validate if the return is correctly"""
    self.assertNotEquals(self.openoffice.pid(), None)
    self.openoffice.stop()
    self.assertEquals(self.openoffice.pid(), None)
    self.assertEquals(self.openoffice.status(), False)

  def testOpenOfficeStart(self):
    """Test if the start method works correclty"""
    self.assertTrue(self.openoffice.status())

  def testOpenOfficeStop(self):
    """Test if the stop method works correctly"""
    self.openoffice.stop()
    waitStopDaemon(self.openoffice)
    self.assertEquals(self.openoffice.status(), False)

  def testOpenOfficeRequest(self):
    """Test if the requisition amount is increasing right"""
    self.openoffice.acquire()
    self.assertEquals(self.openoffice.request, 1)
    self.openoffice.release()

  def testOpenOfficeRestart(self):
    """Test if the method restart works correctly"""
    self.openoffice.restart()
    self.assertTrue(self.openoffice.status())

  def testOpenOfficeLock(self):
    """Test lock and unlock"""
    self.openoffice.acquire()
    self.assertTrue(self.openoffice.isLocked())
    self.openoffice.release()
    self.assertEquals(self.openoffice.isLocked(), False)

  def testStartTwoOpenOfficeWithTheSameAddress(self):
    """Check if starting two openoffice using the same address, the second
    openoffice will terminate the first"""
    second_openoffice = OpenOffice()
    second_openoffice.loadSettings("localhost", 4090,
                                self.working_path,
                                self.office_binary_path,
                                self.uno_path,
                                'en')
    second_openoffice.start()
    self.assertEquals(self.openoffice.status(), False)
    self.assertTrue(second_openoffice.status())
    second_openoffice.stop()

    self.openoffice.start()
    second_openoffice = OpenOffice()
    second_openoffice.loadSettings("localhost", 4091,
                                self.working_path,
                                self.office_binary_path,
                                self.uno_path,
                                'en')
    second_openoffice.start()
    self.assertTrue(self.openoffice.status())
    self.assertTrue(second_openoffice.status())


def test_suite():
  return make_suite(TestOpenOffice)
