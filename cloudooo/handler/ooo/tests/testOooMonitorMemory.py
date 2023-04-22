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
from cloudooo.handler.ooo.monitor.memory import MonitorMemory
from psutil import Process

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
    """Test the monitor with limit of 400Mb to the OpenOffice process"""
    try:
      self.monitor = MonitorMemory(openoffice, 1, 400)
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
      self.assertEqual(openoffice.status(), False)
    finally:
      self.monitor.terminate()

  def testMonitorWithOpenOfficeStopped(self):
    """Tests if the monitor continues to run even with openoffice stopped"""
    openoffice.stop()
    self.monitor = MonitorMemory(openoffice, 2, 400)
    self.monitor.start()
    try:
      sleep(self.interval)
      self.assertTrue(self.monitor.is_alive())
    finally:
      self.monitor.terminate()

  def testCreateProcess(self):
    """Test if the psutil.Process is create correctly"""
    self.monitor = MonitorMemory(openoffice, 2, 400)
    self.monitor.create_process()
    self.assertTrue(hasattr(self.monitor, 'process'))
    self.assertIsInstance(self.monitor.process, Process)

  def testGetMemoryUsage(self):
    """Test memory usage"""
    self.monitor = MonitorMemory(openoffice, 2, 400)
    openoffice.stop()
    memory_usage_int = self.monitor.get_memory_usage()
    self.assertEqual(memory_usage_int, 0)
    if not openoffice.status():
      openoffice.start()
    memory_usage_int = self.monitor.get_memory_usage()
    self.assertIsInstance(memory_usage_int, int)


