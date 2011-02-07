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

import pkg_resources
import psutil
from os.path import exists, join
from subprocess import Popen, PIPE
from threading import Lock
from zope.interface import implements
from application import Application
from cloudooo.interfaces.lockable import ILockable
from cloudooo.utils.utils import logger, convertStringToBool
from cloudooo.handler.ooo.utils.utils import waitStartDaemon, \
                                      removeDirectory, waitStopDaemon, \
                                      socketStatus

class OpenOffice(Application):
  """Object to control one OOo Instance and all features instance."""

  implements(ILockable)

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
    logger.debug("Test OpenOffice %s - Pid %s" % (self.getAddress()[-1],
                                                  self.pid()))
    python = join(self.office_binary_path, "python")
    args = [exists(python) and python or "python",
            pkg_resources.resource_filename("cloudooo",
                                      join('handler', 'ooo',
                                           "helper", "openoffice_tester.py")),
            "--hostname=%s" % host,
            "--port=%s" % port,
            "--uno_path=%s" % self.uno_path]
    logger.debug("Testing Openoffice Instance %s" % port)
    stdout, stderr = Popen(args, stdout=PIPE,
        stderr=PIPE, close_fds=True).communicate()
    stdout_bool = convertStringToBool(stdout.replace("\n", ""))
    if stdout_bool and stderr != "":
      logger.debug("%s\n%s" % (stderr, stdout))
      return False
    else:
      logger.debug("Instance %s works" % port)
      return True

  def _cleanRequest(self):
    """Define request attribute as 0"""
    self.request = 0

  def loadSettings(self, hostname, port, path_run_dir,
                   office_binary_path, uno_path, default_language,
                   environment_dict=None, **kw):
    """Method to load the configuratio to control one OpenOffice Instance
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
      self.process = Popen(command,
                           close_fds=True,
                           env=env)
      if not waitStartDaemon(self, self.timeout):
        continue
      if self._testOpenOffice(self.hostname, self.port):
        return

  def _releaseOpenOfficePort(self):
    for process in psutil.process_iter():
      try:
        if process.exe == join(self.office_binary_path, self._bin_soffice):
          for connection in process.get_connections():
            if connection.status == "LISTEN" and \
                connection.local_address[1] == self.port:
              process.terminate()
      except psutil.error.AccessDenied, e:
        pass
      except TypeError, e:
        # exception to prevent one psutil issue with zombie processes
        logger.debug(e)
      except NotImplementedError, e:
        logger.error("lsof isn't installed on this machine: " + str(e))

  def start(self):
    """Start Instance."""
    self.path_user_installation = join(self.path_run_dir, \
        "cloudooo_instance_%s" % self.port)
    if exists(self.path_user_installation):
      removeDirectory(self.path_user_installation)
    # Create command with all parameters to start the instance
    self.command = [join(self.office_binary_path, self._bin_soffice),
         '-headless',
         '-invisible',
         '-nologo',
         '-nodefault',
         '-norestore',
         '-nofirststartwizard',
         '-accept=socket,host=%s,port=%d;urp;' % (self.hostname, self.port),
         '-env:UserInstallation=file://%s' % self.path_user_installation,
         '-language=%s' % self.default_language,
         ]
    # To run soffice.bin, several environment variables should be set.
    env = self.environment_dict.copy()
    env["LANG"] = "UTF-8"
    env["HOME"] = self.path_user_installation
    env["TMP"] = self.path_user_installation
    env["TMPDIR"] = self.path_user_installation
    self._startProcess(self.command, env)
    self._cleanRequest()
    Application.start(self)

  def stop(self):
    """Stop the instance by pid. By the default
    the signal is 15."""
    Application.stop(self)
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
    logger.debug("OpenOffice %s, %s unlocked" % self.getAddress())
    self._lock.release()

openoffice = OpenOffice()
