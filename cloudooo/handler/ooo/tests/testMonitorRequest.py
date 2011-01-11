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

from time import sleep
from cloudooo.handler.ooo.monitor.request import MonitorRequest
from cloudoooTestCase import CloudoooTestCase, make_suite
from cloudooo.handler.ooo.application.openoffice import openoffice

OPENOFFICE = True

class TestMonitorRequest(CloudoooTestCase):
  """Test all features of a monitor following the interface"""

  def testMonitorTerminate(self):
    """Test terminate function to stop the thread"""
    monitor_request = MonitorRequest(openoffice, 0, 2)
    monitor_request.start()
    self.assertTrue(monitor_request.is_alive())
    monitor_request.terminate()
    sleep(4)
    try:
      self.assertEquals(monitor_request.is_alive(), False)
    finally:
      monitor_request.terminate()

  def testMonitorRequest(self):
    """Test if openoffice is monitored correclty"""
    openoffice.request = 3
    self.assertEquals(openoffice.request, 3)
    monitor_request = MonitorRequest(openoffice, 1, 2)
    monitor_request.start()
    sleep(4)
    self.assertEquals(openoffice.request, 0)
    monitor_request.terminate()


def test_suite():
  return make_suite(TestMonitorRequest)
