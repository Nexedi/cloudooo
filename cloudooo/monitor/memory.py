##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
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

from cloudooo.monitor.monitor import Monitor
from threading import Thread
from psutil import Process
from cloudooo.utils import logger
from time import sleep

class MonitorMemory(Monitor, Thread):
  """Usefull to control the memory and does not allow use it unnecessarily"""
  
  def __init__(self, openoffice, interval, limit_memory_usage):
    """Expects to receive an object that implements the interfaces IApplication
    and ILockable, the limit of memory usage that the openoffice can use and the
    interval to check the object."""
    Monitor.__init__(self, openoffice, interval)
    Thread.__init__(self)
    self.limit = limit_memory_usage

  def create_process(self):
    self.process = Process(int(self.openoffice.pid()))

  def get_memory_usage(self):
    try:
      if not hasattr(self, 'process'):
        self.create_process()
      elif self.process.pid != int(self.openoffice.pid()):
        self.create_process()
    except TypeError:
      logger.debug("OpenOffice is stopped")
      return 0
    # convert bytes to GB
    return sum(self.process.get_memory_info())/(1024*1024)

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
