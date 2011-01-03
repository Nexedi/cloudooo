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
from multiprocessing import Process
from time import sleep
from cloudooo.utils.utils import logger


class MonitorTimeout(Monitor, Process):
  """Monitors and controls the time of use of an object"""

  def __init__(self, openoffice, interval):
    """Expects to receive an object that implements the interfaces IApplication
    and ILockable. And the interval to check the object."""
    Monitor.__init__(self, openoffice, interval)
    Process.__init__(self)

  def run(self):
    """Start the process"""
    port = self.openoffice.getAddress()[-1]
    pid = self.openoffice.pid()
    logger.debug("Monitoring OpenOffice: Port %s, Pid: %s" % (port, pid))
    self.status_flag = True
    sleep(self.interval)
    if self.openoffice.isLocked():
      logger.debug("Stop OpenOffice - Port %s - Pid %s" % (port, pid))
      self.openoffice.stop()

  def terminate(self):
    """Stop the process"""
    Monitor.terminate(self)
    Process.terminate(self)
