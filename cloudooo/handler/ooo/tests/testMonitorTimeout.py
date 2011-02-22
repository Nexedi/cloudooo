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
from time import sleep
from cloudooo.handler.ooo.application.openoffice import openoffice
from cloudooo.handler.ooo.monitor.timeout import MonitorTimeout
from cloudooo.handler.tests.handlerTestCase import make_suite

OPENOFFICE = True


class TestMonitorTimeout(unittest.TestCase):
  """Test all features of a monitor following the interface"""

  def _createMonitor(self, interval):
    """Returns an MonitorTimeout instance"""
    return MonitorTimeout(openoffice, interval)

  def testMonitorTimeoutStatus(self):
    """Test if the monitor of memory works"""
    monitor_timeout = self._createMonitor(10)
    monitor_timeout.start()
    self.assertTrue(monitor_timeout.is_alive())
    monitor_timeout.terminate()
    monitor_timeout = self._createMonitor(1)
    monitor_timeout.start()
    sleep(2)
    self.assertEquals(monitor_timeout.is_alive(), False)
    monitor_timeout.terminate()

  def testStopOpenOffice(self):
    """Test if the openoffice stop by the monitor"""
    openoffice.acquire()
    try:
      monitor_timeout = self._createMonitor(1)
      monitor_timeout.start()
      sleep(2)
      self.assertEquals(openoffice.status(), False)
      openoffice.restart()
      self.assertTrue(openoffice.status())
    finally:
      monitor_timeout.terminate()
      openoffice.release()

  def testStopOpenOfficeTwice(self):
    """Test the cases that is necessary start the monitors twice"""
    openoffice.acquire()
    try:
      monitor_timeout = self._createMonitor(1)
      monitor_timeout.start()
      sleep(2)
      self.assertEquals(openoffice.status(), False)
      monitor_timeout.terminate()
      openoffice.restart()
      self.assertTrue(openoffice.status())
      monitor_timeout = self._createMonitor(1)
      monitor_timeout.start()
      sleep(2)
      self.assertEquals(openoffice.status(), False)
      monitor_timeout.terminate()
      sleep(1)
      self.assertEquals(monitor_timeout.is_alive(), False)
    finally:
      monitor_timeout.terminate()
      openoffice.release()


def test_suite():
  return make_suite(TestMonitorTimeout)
