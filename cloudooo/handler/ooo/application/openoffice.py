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

import pkg_resources
import psutil
import subprocess
from psutil import AccessDenied, NoSuchProcess
from os.path import exists, join
from threading import Lock
from zope.interface import implementer
from .application import Application
from cloudooo.interfaces.lockable import ILockable
from cloudooo.util import logger
from cloudooo.handler.ooo.util import waitStartDaemon, \
                                      removeDirectory, waitStopDaemon, \
                                      socketStatus


@implementer(ILockable)
class OpenOffice(Application):
  """Object to control one OOo Instance and all features instance."""

  name = "openoffice"

  def __init__(self):
    """Creates the variable to save the pid, port and hostname of the object.
    The lock is a simple lock python that is used when one requisition is
    using the openoffice.
    """
    self._bin_soffice = 'soffice.bin'
    self._lock = Lock()
    self._cleanRequest()

  def _testOpenOffice(self, host, port):
    """Test if OpenOffice was started correctly"""
    logger.debug(
      "Test OpenOffice %s - Pid %s",
      self.getAddress()[-1],
      self.pid())
    python = join(self.office_binary_path, "python")
    args = [exists(python) and python or "python3",
            pkg_resources.resource_filename("cloudooo",
                                      join('handler', 'ooo',
                                           "helper", "openoffice_tester.py")),
            "--hostname=%s" % host,
            "--port=%s" % port,
            "--uno_path=%s" % self.uno_path]
    logger.debug("Testing Openoffice Instance %s", port)
    try:
      subprocess.check_output(args, stderr=subprocess.STDOUT, close_fds=True)
    except subprocess.CalledProcessError as e:
      logger.warning(e.output)
      return False
    else:
      logger.debug("Instance %s works", port)
      return True

  def _cleanRequest(self):
    """Define request attribute as 0"""
    self.request = 0

  def loadSettings(self, hostname, port, path_run_dir,
                   office_binary_path, uno_path, default_language,
                   environment_dict=None, **kw):
    """Method to load the configuration to control one OpenOffice Instance
    Keyword arguments:
    office_path -- Full Path of the OOo executable.
      e.g office_binary_path='/opt/openoffice.org3/program'
    uno_path -- Full path of the Uno Library
    """
    if environment_dict is None:
      environment_dict = {}
    Application.loadSettings(self, hostname, port, path_run_dir)
    self.office_binary_path = office_binary_path
    self.uno_path = uno_path
    self.default_language = default_language
    self.environment_dict = environment_dict

  def _startProcess(self, command, env):
    """Start OpenOffice.org process"""
    for i in range(5):
      self.stop()
      waitStopDaemon(self, self.timeout)
      self.process = subprocess.Popen(command, close_fds=True, env=env)
      if not waitStartDaemon(self, self.timeout):
        continue
      if self._testOpenOffice(self.hostname, self.port):
        return

  def _releaseOpenOfficePort(self):
    openoffice_exe = join(self.office_binary_path, self._bin_soffice)
    for process in psutil.process_iter():
      try:
        if process.exe() == openoffice_exe:
          for connection in process.connections():
            if connection.status == "LISTEN" and \
                connection.laddr[1] == self.port:
              process.terminate()
      except (NoSuchProcess, AccessDenied):
        pass
      except Exception:
        logger.error("Unexpected error releasing openoffice port", exc_info=True)

  def start(self, init=True):
    """Start Instance."""
    self.path_user_installation = join(self.path_run_dir, \
        "cloudooo_instance_%s" % self.port)
    if init and exists(self.path_user_installation):
      removeDirectory(self.path_user_installation)
    # Create command with all parameters to start the instance
    self.command = [join(self.office_binary_path, self._bin_soffice),
         '--headless',
         '--invisible',
         '--nocrashreport',
         '--nologo',
         '--nodefault',
         '--norestore',
         '--nofirststartwizard',
         '--accept=socket,host=%s,port=%d;urp;' % (self.hostname, self.port),
         '-env:UserInstallation=file://%s' % self.path_user_installation,
         '--language=%s' % self.default_language,
         ]
    # To run soffice.bin, several environment variables should be set.
    env = self.environment_dict.copy()
    env.setdefault("LANG", "en_US.UTF-8")
    env["HOME"] = self.path_user_installation
    env["TMP"] = self.path_user_installation
    env["TMPDIR"] = self.path_user_installation
    self._startProcess(self.command, env)
    self._cleanRequest()
    super().start()

  def stop(self):
    """Stop the instance by pid. By the default
    the signal is 15."""
    super().stop()
    if socketStatus(self.hostname, self.port):
      self._releaseOpenOfficePort()
    self._cleanRequest()

  def isLocked(self):
    """Verify if OOo instance is being used."""
    return self._lock.locked()

  def acquire(self):
    """Lock Instance to use."""
    self.request += 1
    self._lock.acquire()

  def release(self):
    """Unlock Instance."""
    logger.debug("OpenOffice %s, %s unlocked", *self.getAddress())
    self._lock.release()

openoffice = OpenOffice()
