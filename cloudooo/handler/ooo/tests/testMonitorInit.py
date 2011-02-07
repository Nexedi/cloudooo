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

import cloudooo.handler.ooo.monitor as monitor
from cloudoooTestCase import CloudoooTestCase, make_suite
from cloudooo.handler.ooo.monitor.request import MonitorRequest
from cloudooo.handler.ooo.monitor.memory import MonitorMemory

OPENOFFICE = True

class TestMonitorInit(CloudoooTestCase):
  """Test Case to test if the monitors are controlled correctly"""

  def afterSetUp(self):
    """Create one fake file configuration"""
    self.load_config = {}
    self.load_config['monitor_interval'] = 1
    self.load_config['limit_number_request'] = 100
    self.load_config['limit_memory_used'] = 500

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
    self.load_config['enable_memory_monitor'] = True
    monitor.load(self.load_config)
    self.assertEquals(isinstance(monitor.monitor_request,
                                 MonitorRequest),
                                 True)
    self.assertEquals(isinstance(monitor.monitor_memory,
                                 MonitorMemory),
                                 True)


def test_suite():
  return make_suite(TestMonitorInit)

