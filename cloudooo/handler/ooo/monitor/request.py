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

from .monitor import Monitor
from threading import Thread
from cloudooo.util import logger
from time import sleep


class MonitorRequest(Monitor, Thread):
  """Usefull to control the number of request in Object"""

  def __init__(self, openoffice, interval, request_limit):
    """Expects to receive an object that implements the interfaces IApplication
    and ILockable, the limit of request that the openoffice can receive and the
    interval to check the object."""
    Monitor.__init__(self, openoffice, interval)
    Thread.__init__(self)
    self.request_limit = request_limit

  def start(self):
    self.status_flag = True
    Thread.start(self)

  def run(self):
    """Is called by start function"""
    logger.debug("Start MonitorRequest")
    while self.status_flag:
      if self.openoffice.request > self.request_limit:
        self.openoffice.acquire()
        logger.debug("Openoffice: %s, %s will be restarted",
          *self.openoffice.getAddress())
        self.openoffice.restart()
        self.openoffice.release()
      sleep(self.interval)
    logger.debug("Stop MonitorRequest ")
