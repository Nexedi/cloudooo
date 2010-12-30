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
from cloudoooTestCase import cloudoooTestCase
from cloudooo.application.openoffice import OpenOffice
from cloudoooTestCase import make_suite
from cloudooo.utils import waitStopDaemon
from psutil import Process, AccessDenied


class TestOpenOffice(cloudoooTestCase):
  """Test OpenOffice object and manipulation of OOo Instance"""
  
  def afterSetUp(self):
    """Instantiate one OpenOffice"""
    self.openoffice = OpenOffice()
    self.openoffice.loadSettings("localhost", 4090,
                                self.working_path,
                                self.virtual_display_id,
                                self.office_binary_path,
                                self.uno_path)
    self.openoffice.start()

  def tearDown(self):
    """Stop the OpenOffice"""
    if self.openoffice.status():
      self.openoffice.stop()

  def testPid(self):
    """Test pid function to validate if the return is correctly"""
    self.assertNotEquals(self.openoffice.pid(), None)
    self.openoffice.stop()
    waitStopDaemon(self.openoffice)
    self.assertEquals(self.openoffice.pid(), None)

  def testOpenOfficeStart(self):
    """Test if the start method works correclty"""
    self.assertEquals(self.openoffice.status(), True)

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
    self.assertEquals(self.openoffice.status(), True)

  def testOpenOfficeLock(self):
    """Test lock and unlock"""
    self.openoffice.acquire()
    self.assertEquals(self.openoffice.isLocked(), True)
    self.openoffice.release()
    self.assertEquals(self.openoffice.isLocked(), False)

  def testStartTwoOpenOfficeWithTheSameAddress(self):
    """Check if starting two openoffice using the same address, the second
    openoffice will terminate the first"""
    second_openoffice = OpenOffice()
    second_openoffice.loadSettings("localhost", 4090,
                                self.working_path,
                                self.virtual_display_id,
                                self.office_binary_path,
                                self.uno_path)
    try:
      second_openoffice.start()
      try:
        openoffice_process = Process(self.openoffice.pid())
        openoffice_process.get_connections()
        self.fail("Access get_connections() function should fails")
      except AccessDenied:
        self.assertTrue("Excepted failure")
    finally:
      second_openoffice.stop()

    self.openoffice.start()
    second_openoffice = OpenOffice()
    second_openoffice.loadSettings("localhost", 4091,
                                self.working_path + "_",
                                self.virtual_display_id,
                                self.office_binary_path,
                                self.uno_path)
    try:
      second_openoffice.start()
      try:
        openoffice_process = Process(self.openoffice.pid())
        connection = openoffice_process.get_connections()[0]
        self.assertEquals(connection.local_address[1], 4090)
        openoffice_process = Process(second_openoffice.pid())
        connection = openoffice_process.get_connections()[0]
        self.assertEquals(connection.local_address[1], 4091)
      except AccessDenied:
        self.fail("Access get_connections() function should be allowed")
    finally:
      second_openoffice.stop()

    if not self.openoffice.status():
      self.openoffice.start()
    second_openoffice = OpenOffice()
    second_openoffice.loadSettings("localhost", 40900,
                                self.working_path + "_",
                                self.virtual_display_id,
                                self.office_binary_path,
                                self.uno_path)
    second_openoffice.start()

    third_openoffice = OpenOffice()
    third_openoffice.loadSettings("localhost", 40900,
                                self.working_path + "_",
                                self.virtual_display_id,
                                self.office_binary_path,
                                self.uno_path)

    try:
      third_openoffice.start()
      try:
        openoffice_process = Process(self.openoffice.pid())
        connection = openoffice_process.get_connections()[0]
        self.assertEquals(connection.local_address[1], 4090)
        openoffice_process = Process(second_openoffice.pid())
        openoffice_process.get_connections()
        self.fail("Access get_connections() function should fails")
      except AccessDenied:
        self.assertTrue("Excepted failure")
    finally:
      second_openoffice.stop()
      third_openoffice.stop()


def test_suite():
  return make_suite(TestOpenOffice)

if __name__ == "__main__":
  from cloudoooTestCase import startFakeEnvironment, stopFakeEnvironment
  startFakeEnvironment(False)
  suite = unittest.TestLoader().loadTestsFromTestCase(TestOpenOffice)
  unittest.TextTestRunner(verbosity=2).run(suite)
  stopFakeEnvironment()
