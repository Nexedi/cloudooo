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

import sys
import json
import pkg_resources
from cloudooo.handler.ooo.application.openoffice import openoffice
from subprocess import Popen, PIPE
from os import environ, path
from cloudooo.tests.handlerTestCase import HandlerTestCase
from time import sleep

OPENOFFICE = True


class TestUnoOfficeTester(HandlerTestCase):
  """Test Case to test all features of script openoffice_tester.py"""

  def afterSetUp(self):
    """ """
    self.package_namespace = "cloudooo.handler.ooo"
    environ['uno_path'] = ''
    environ['office_binary_path'] = ''
    if 'PYTHONPATH' in environ:
      del environ['PYTHONPATH']
    if self.uno_path in sys.path:
      sys.path.remove(self.uno_path)
    openoffice.acquire()

  def tearDown(self):
    """ """
    environ['uno_path'] = self.uno_path
    environ['office_binary_path'] = self.office_binary_path
    openoffice.release()

  def testWithOpenOffice(self):
    """Test when the openoffice is started"""
    python = path.join(self.office_binary_path, "python")
    command = [path.exists(python) and python or "python",
            pkg_resources.resource_filename(self.package_namespace,
                                       "/helper/openoffice_tester.py"),
            "--uno_path=%s" % self.uno_path,
            "--office_binary_path=%s" % self.office_binary_path,
            "--connection=%s" % openoffice.getConnection()]
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    self.assertEquals(process.returncode, -3)
    self.assertEquals(stderr, '', stderr)
    result = json.loads(stdout)
    self.assertTrue(result)

  def testWithoutOpenOffice(self):
    """Test when the openoffice is stopped"""
    openoffice.stop()
    python = path.join(self.office_binary_path, "python")
    command = [path.exists(python) and python or "python",
            pkg_resources.resource_filename(self.package_namespace,
                                            "/helper/openoffice_tester.py"),
            "--uno_path=%s" % self.uno_path,
            "--office_binary_path=%s" % self.office_binary_path,
            "--connection=%s" % openoffice.getConnection()]
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    self.assertEquals(process.returncode, -3)
    self.assertEquals(stderr, '', stderr)
    result = json.loads(stdout)
    self.assertFalse(result)
    openoffice.start()

  def testExceptionNotify(self):
    """Test correctly notify about issues"""
    exception = "ModuleNotFoundError: No module named"
    exception1 = "ImportError:"
    command = ["python",
            pkg_resources.resource_filename(self.package_namespace,
                                            "/helper/openoffice_tester.py"),
            "--uno_path=%s" % self.uno_path + "not_exist_folder",
            "--office_binary_path=%s" % self.office_binary_path,
            "--connection=%s" % openoffice.getConnection()]
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    self.assertEquals(process.returncode, -3)
    self.assertEquals(stdout, '', stdout)
    self.assertTrue((exception in stderr) or (exception1 in stderr), stderr)

  def testOpenOfficeTermination(self):
    """Test termination when the openoffice is started"""
    python = path.join(self.office_binary_path, "python")
    self.assertTrue(path.exists(openoffice.lock_file), "libreoffice not started - lock_file is not exist")
    command = [path.exists(python) and python or "python",
            pkg_resources.resource_filename(self.package_namespace,
                                            "/helper/openoffice_tester.py"),
            "--uno_path=%s" % self.uno_path,
            "--office_binary_path=%s" % self.office_binary_path,
            "--connection=%s" % openoffice.getConnection(),
            "--terminate"]
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    for num in range(5):
      if not path.exists(openoffice.lock_file):
        break
      sleep(1)
    self.assertEquals(process.returncode, -3)
    self.assertEquals(stderr, '', stderr)
    result = json.loads(stdout)
    self.assertTrue(result)
    self.assertFalse(path.exists(openoffice.lock_file), "libreoffice not correctly stopped - lock_file exist")
    openoffice.start()

  def testOpenOfficeTerminationIfStoped(self):
    """Test termination when the openoffice is stopped"""
    openoffice.stop()
    self.assertFalse(path.exists(openoffice.lock_file), "libreoffice not correctly stopped - lock_file exist")
    python = path.join(self.office_binary_path, "python")
    command = [path.exists(python) and python or "python",
            pkg_resources.resource_filename(self.package_namespace,
                                            "/helper/openoffice_tester.py"),
            "--uno_path=%s" % self.uno_path,
            "--office_binary_path=%s" % self.office_binary_path,
            "--connection=%s" % openoffice.getConnection(),
            "--terminate"]
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    for num in range(5):
      if not path.exists(openoffice.lock_file):
        break
      sleep(1)
    self.assertEquals(process.returncode, -3)
    self.assertEquals(stderr, '', stderr)
    result = json.loads(stdout)
    self.assertFalse(result)
    self.assertFalse(path.exists(openoffice.lock_file), "libreoffice not correctly stopped - lock_file exist")
    openoffice.start()
