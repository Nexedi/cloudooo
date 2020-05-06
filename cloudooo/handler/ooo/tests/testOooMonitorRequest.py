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

from time import sleep
from cloudooo.handler.ooo.monitor.request import MonitorRequest
from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite
from cloudooo.handler.ooo.application.openoffice import openoffice

OPENOFFICE = True


class TestMonitorRequest(HandlerTestCase):
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


