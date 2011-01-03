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

from monitor import Monitor
from threading import Thread
from cloudooo.utils.utils import logger
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
        logger.debug("Openoffice: %s, %s will be restarted" % \
          self.openoffice.getAddress())
        self.openoffice.restart()
        self.openoffice.release()
      sleep(self.interval)
    logger.debug("Stop MonitorRequest ")
