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

import cloudooo.handler.ooo.monitor as monitor
from cloudooo.tests.handlerTestCase import HandlerTestCase
from cloudooo.handler.ooo.monitor.request import MonitorRequest
from cloudooo.handler.ooo.monitor.memory import MonitorMemory

OPENOFFICE = True


class TestMonitorInit(HandlerTestCase):
  """Test Case to test if the monitors are controlled correctly"""

  def afterSetUp(self):
    """Create one fake file configuration"""
    self.load_config = {
      'monitor_interval': '1',
      'limit_number_request': '100',
      'limit_memory_used': '500',
    }

  def tearDown(self):
    """stop all monitors"""
    monitor.stop()

  def testMonitorInitGlobalAttributes(self):
    """Test the global attributes"""
    self.assertEquals(monitor.monitor_request, None)
    self.assertEquals(monitor.monitor_memory, None)

  def testMonitorLoadOnlyMonitorRequest(self):
    """Check if the monitors are started"""
    monitor.load(self.load_config)
    self.assertEquals(isinstance(monitor.monitor_request,
                                MonitorRequest),
                                True)

  def testMonitorLoadMonitorMemory(self):
    """Check if the MemoryMemory is started"""
    self.load_config['enable_memory_monitor'] = 'true'
    monitor.load(self.load_config)
    self.assertEquals(isinstance(monitor.monitor_request,
                                 MonitorRequest),
                                 True)
    self.assertEquals(isinstance(monitor.monitor_memory,
                                 MonitorMemory),
                                 True)


