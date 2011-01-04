##############################################################################
#
# Copyright (c) 2009-2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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
import psutil
from cloudooo.utils.utils import logger
from time import sleep, time


class MonitorSpleepingTime(Monitor, Thread):
  """Usefull to stop daemon if not beeing used after duration of time
  """

  def __init__(self, openoffice, interval, sleeping_time):
    """Expects to receive an object that implements the interfaces IApplication
    and ILockable, the limit of memory usage that the openoffice can use and
    the interval to check the object."""
    Monitor.__init__(self, openoffice, interval)
    Thread.__init__(self)
    self.sleeping_time = sleeping_time
    self._touched_at = time()

  def start(self):
    self.status_flag = True
    Thread.start(self)

  def touch(self):
    """Restart countdown
    """
    logger.debug("Touch MonitorSpleepingTime")
    self._touched_at = time()

  def run(self):
    """Start monitoring process.
    Stop daemon if running and not touch after sleeping duration
    """
    logger.debug("Start MonitorSpleepingTime")
    while self.status_flag:
      current_time = time()
      if self.openoffice.status() and\
        (self._touched_at + self.sleeping_time) <= current_time:
        logger.debug("Stopping OpenOffice after sleeping time of %is" %\
                                                            self.sleeping_time)
        self.openoffice.acquire()
        self.openoffice.stop()
        self.openoffice.release()
      sleep(self.interval)
    logger.debug("Stop MonitorSpleepingTime")

