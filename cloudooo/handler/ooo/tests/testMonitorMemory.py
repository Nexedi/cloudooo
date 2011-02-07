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
from cloudooo.handler.ooo.monitor.memory import MonitorMemory
from psutil import Process
from types import IntType
from cloudoooTestCase import make_suite

OPENOFFICE = True

class TestMonitorMemory(unittest.TestCase):
  """Test case to see if the MonitorMemory is properly managing the
  openoffice."""

  interval = 3

  def setUp(self):
    if not openoffice.status():
      openoffice.start()

  def tearDown(self):
    """Restart the openoffice in cases that the openoffice is stopped"""
    if not openoffice.status():
      openoffice.acquire()
      openoffice.restart()
      openoffice.release()
    if self.monitor.is_alive():
      self.monitor.terminate()

  def testMonitorWithHugeMemoryLimit(self):
    """Test the monitor with limit of 1Gb to the OpenOffice process"""
    try:
      self.monitor = MonitorMemory(openoffice, 1, 1000)
      self.monitor.start()
      sleep(6)
      self.assertTrue(openoffice.status())
    finally:
      self.monitor.terminate()

  def testMonitorWithLittleMemoryLimit(self):
    """Test the monitor with limit of 10Mb. In This case the openoffice will be
    stopped"""
    try:
      self.monitor = MonitorMemory(openoffice, 2, 10)
      self.monitor.start()
      sleep(self.interval)
      self.assertEquals(openoffice.status(), False)
    finally:
      self.monitor.terminate()

  def testMonitorWithOpenOfficeStopped(self):
    """Tests if the monitor continues to run even with openoffice stopped"""
    openoffice.stop()
    self.monitor = MonitorMemory(openoffice, 2, 1000)
    self.monitor.start()
    try:
      sleep(self.interval)
      self.assertTrue(self.monitor.is_alive())
    finally:
      self.monitor.terminate()

  def testCreateProcess(self):
    """Test if the psutil.Process is create correctly"""
    self.monitor = MonitorMemory(openoffice, 2, 1000)
    self.monitor.create_process()
    self.assertTrue(hasattr(self.monitor, 'process'))
    self.assertEquals(type(self.monitor.process), Process)

  def testGetMemoryUsage(self):
    """Test memory usage"""
    self.monitor = MonitorMemory(openoffice, 2, 1000)
    openoffice.stop()
    memory_usage_int = self.monitor.get_memory_usage()
    self.assertEquals(memory_usage_int, 0)
    if not openoffice.status():
      openoffice.start()
    memory_usage_int = self.monitor.get_memory_usage()
    self.assertEquals(type(memory_usage_int), IntType)


def test_suite():
  return make_suite(TestMonitorMemory)

