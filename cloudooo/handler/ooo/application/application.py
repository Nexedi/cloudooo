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

from zope.interface import implements
from cloudooo.interfaces.application import IApplication
from cloudooo.util import logger
from psutil import pid_exists, Process, TimeoutExpired, NoSuchProcess


class Application(object):
  """Base object to create an object that is possible manipulation a
  process"""

  implements(IApplication)

  name = "application"

  def start(self, init=True):
    """Start Application"""
    logger.debug("Process Started %s, Port %s. Pid %s" % (self.name,
                                                    self.getAddress()[-1],
                                                    self.pid()))

  def stopProcess(self, process_pid):
    """Stop the process"""
    error = False
    logger.debug("Stop Pid - %s", process_pid)
    returncode = None
    try:
      process = Process(process_pid)
      cmdline = " ".join(process.cmdline())
      process.terminate()
      returncode = process.wait(self.timeout)
    except NoSuchProcess:
      pass
    except TimeoutExpired:
      error = True
      logger.error("Process %s survived SIGTERM after %s", process_pid, self.timeout)
      try:
        process.kill()
        returncode = process.wait(self.timeout)
      except NoSuchProcess:
        pass
      except TimeoutExpired:
        logger.error("Process %s survived SIGKILL after %s", process_pid, self.timeout)
    if error and returncode:
      logger.error("Process %s cmdline: %s ended with returncode %s", process_pid, cmdline, returncode)
    elif returncode != 0:
      logger.debug("Process %s ended with returncode %s", process_pid, returncode)

  def stop(self):
    if hasattr(self, 'process'):
      self.stopProcess(self.process.pid)
      delattr(self, "process")

  def loadSettings(self, hostname, port, path_run_dir, **kwargs):
    """Define attributes for application instance
    Keyword arguments:
    hostname -- Host to start the instance.
    port -- Expected a int number.
    path_run_dir -- Full path to create the enviroment.
    """
    self.hostname = hostname
    self.port = port
    self.path_run_dir = path_run_dir
    self.timeout = kwargs.get('start_timeout', 20)

  def restart(self):
    """Start and Stop the process"""
    self.stop()
    self.start(init=False)

  def status(self):
    """Check by socket if the openoffice work."""
    pid = self.pid()
    if pid is None or not pid_exists(pid):
      return False
    return True

  def getAddress(self):
    """Return port and hostname of OOo Instance."""
    return self.hostname, self.port

  def pid(self):
    """Returns the pid"""
    if not hasattr(self, 'process'):
      return None
    return self.process.pid
