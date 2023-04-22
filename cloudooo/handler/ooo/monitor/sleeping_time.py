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

from monitor import Monitor
from threading import Thread
from cloudooo.util import logger
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
        logger.debug("Stopping OpenOffice after sleeping time of %is",
                      self.sleeping_time)
        self.openoffice.acquire()
        self.openoffice.stop()
        self.openoffice.release()
      sleep(self.interval)
    logger.debug("Stop MonitorSpleepingTime")
