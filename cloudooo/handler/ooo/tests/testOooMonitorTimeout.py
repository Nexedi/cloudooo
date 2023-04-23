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

import unittest
from time import sleep
from cloudooo.handler.ooo.application.openoffice import openoffice
from cloudooo.handler.ooo.monitor.timeout import MonitorTimeout

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
    self.assertEqual(monitor_timeout.is_alive(), False)
    monitor_timeout.terminate()

  def testStopOpenOffice(self):
    """Test if the openoffice stop by the monitor"""
    openoffice.acquire()
    try:
      monitor_timeout = self._createMonitor(1)
      monitor_timeout.start()
      sleep(5)
      self.assertEqual(openoffice.status(), False)
      openoffice.restart()
      self.assertTrue(openoffice.status())
    finally:
      try:
        monitor_timeout.terminate()
      finally:
        openoffice.release()

  def testStopOpenOfficeTwice(self):
    """Test the cases that is necessary start the monitors twice"""
    openoffice.acquire()
    try:
      monitor_timeout = self._createMonitor(1)
      monitor_timeout.start()
      sleep(5)
      self.assertEqual(openoffice.status(), False)
      monitor_timeout.terminate()
      openoffice.restart()
      self.assertTrue(openoffice.status())
      monitor_timeout = self._createMonitor(1)
      monitor_timeout.start()
      sleep(5)
      self.assertEqual(openoffice.status(), False)
      monitor_timeout.terminate()
      sleep(1)
      self.assertEqual(monitor_timeout.is_alive(), False)
    finally:
      try:
        monitor_timeout.terminate()
      finally:
        openoffice.release()


