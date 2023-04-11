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

from cloudooo.tests.handlerTestCase import HandlerTestCase
from cloudooo.handler.ooo.application.openoffice import OpenOffice
from cloudooo.handler.ooo.util import waitStopDaemon

OPENOFFICE = True


class TestOpenOffice(HandlerTestCase):
  """Test OpenOffice object and manipulation of OOo Instance"""

  def afterSetUp(self):
    """Instantiate one OpenOffice"""
    self.openoffice = OpenOffice()
    self.openoffice.loadSettings("localhost", 4090,
                                self.working_path,
                                self.office_binary_path,
                                self.uno_path,
                                'en',
                                self.environment_dict)
    self.openoffice.start()

  def tearDown(self):
    """Stop the OpenOffice"""
    if self.openoffice.status():
      self.openoffice.stop()

  def testPid(self):
    """Test pid function to validate if the return is correctly"""
    self.assertNotEqual(self.openoffice.pid(), None)
    self.openoffice.stop()
    self.assertEqual(self.openoffice.pid(), None)
    self.assertEqual(self.openoffice.status(), False)

  def testOpenOfficeStart(self):
    """Test if the start method works correclty"""
    self.assertTrue(self.openoffice.status())

  def testOpenOfficeStop(self):
    """Test if the stop method works correctly"""
    self.openoffice.stop()
    waitStopDaemon(self.openoffice)
    self.assertEqual(self.openoffice.status(), False)

  def testOpenOfficeRequest(self):
    """Test if the requisition amount is increasing right"""
    self.openoffice.acquire()
    self.assertEqual(self.openoffice.request, 1)
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
    self.assertEqual(self.openoffice.isLocked(), False)

  def testStartTwoOpenOfficeWithTheSameAddress(self):
    """Check if starting two openoffice using the same address, the second
    openoffice will terminate the first"""
    second_openoffice = OpenOffice()
    second_openoffice.loadSettings("localhost", 4090,
                                self.working_path,
                                self.office_binary_path,
                                self.uno_path,
                                'en',
                                self.environment_dict)
    second_openoffice.start()
    self.assertEqual(self.openoffice.status(), False)
    self.assertTrue(second_openoffice.status())
    second_openoffice.stop()

    self.openoffice.start()
    second_openoffice = OpenOffice()
    second_openoffice.loadSettings("localhost", 4091,
                                self.working_path,
                                self.office_binary_path,
                                self.uno_path,
                                'en',
                                self.environment_dict)
    second_openoffice.start()
    self.assertTrue(self.openoffice.status())
    self.assertTrue(second_openoffice.status())
    second_openoffice.stop()
    self.assertFalse(second_openoffice.status())


