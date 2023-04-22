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
from multiprocessing import Process
import psutil
from cloudooo.util import logger
from time import sleep


class MonitorMemory(Monitor, Process):
  """Usefull to control the memory and does not allow use it unnecessarily"""

  def __init__(self, openoffice, interval, limit_memory_usage):
    """Expects to receive an object that implements the interfaces IApplication
    and ILockable, the limit of memory usage that the openoffice can use and
    the interval to check the object."""
    Monitor.__init__(self, openoffice, interval)
    Process.__init__(self)
    self.limit = limit_memory_usage

  def create_process(self):
    self.process = psutil.Process(int(self.openoffice.pid()))

  def get_memory_usage(self):
    try:
      if not hasattr(self, 'process') or \
          self.process.pid != int(self.openoffice.pid()):
        self.create_process()
      return self.process.memory_info().rss // (1024 * 1024)
    except TypeError:
      logger.debug("OpenOffice is stopped")
      return 0
    except psutil.NoSuchProcess:
      # Exception raised when a process with a certain PID doesn't or no longer
      # exists (zombie).
      return 0

  def run(self):
    """Is called by start function. this function is responsible for
    controlling the amount of memory used, and if the process exceeds the limit
    it is stopped forcibly
    """
    self.status_flag = True
    logger.debug("Start MonitorMemory")
    while self.status_flag:
      if self.get_memory_usage() > self.limit:
        logger.debug("Stopping OpenOffice")
        self.openoffice.stop()
      sleep(self.interval)
    logger.debug("Stop MonitorMemory")

  def terminate(self):
    Monitor.terminate(self)
    Process.terminate(self)
