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

from zope.interface import implementer
from cloudooo.interfaces.application import IApplication
from cloudooo.util import logger
from cloudooo.handler.ooo.util import waitStopDaemon
from psutil import pid_exists, Process, AccessDenied


@implementer(IApplication)
class Application(object):
  """Base object to create an object that is possible manipulation a
  process"""

  name = "application"

  def start(self, init=True):
    """Start Application"""
    logger.debug(
      "Process Started %s, Port %s. Pid %s",
      self.name,
      self.getAddress()[-1],
      self.pid())

  def stop(self):
    """Stop the process"""
    if hasattr(self, 'process') and self.status():
      process_pid = self.process.pid
      logger.debug("Stop Pid - %s", process_pid)
      try:
        self.process.terminate()
        waitStopDaemon(self, self.timeout)
      finally:
        if pid_exists(process_pid) or self.status():
          Process(process_pid).kill()
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

    process = Process(pid)
    try:
      for connection in process.connections():
        if connection.status == 'LISTEN' and \
            connection.laddr[1] == self.port:
          return True
    except AccessDenied:
      return False

    return False

  def getAddress(self):
    """Return port and hostname of OOo Instance."""
    return self.hostname, self.port

  def pid(self):
    """Returns the pid"""
    if not hasattr(self, 'process'):
      return None
    return self.process.pid

  def hasExited(self):
    """Check if process has exited running"""
    if not hasattr(self, 'process'):
      return True
    return self.process.poll() is not None
