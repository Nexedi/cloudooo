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

import json
import pkg_resources
from cloudooo.handler.ooo.application.openoffice import openoffice
from subprocess import Popen, PIPE
from os import environ, path
from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite

OPENOFFICE = True


class TestUnoMimeMapper(HandlerTestCase):
  """Test Case to test all features of script unomimemapper"""

  def afterSetUp(self):
    """ """
    self.package_namespace = "cloudooo.handler.ooo"
    environ['uno_path'] = ''
    environ['office_binary_path'] = ''
    openoffice.acquire()

  def tearDown(self):
    """ """
    environ['uno_path'] = self.uno_path
    environ['office_binary_path'] = self.office_binary_path
    openoffice.release()

  def testCreateLocalAttributes(self):
    """Test if filters returns correctly the filters and types in dict"""
    hostname, host = openoffice.getAddress()
    python = path.join(self.office_binary_path, "python")
    command = [path.exists(python) and python or "python",
            pkg_resources.resource_filename(self.package_namespace,
                                       "/helper/unomimemapper.py"),
            "--uno_path=%s" % self.uno_path,
            "--office_binary_path=%s" % self.office_binary_path,
            "--hostname=%s" % self.hostname,
            "--port=%s" % self.openoffice_port]
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    self.assertEquals(process.returncode, -15)
    self.assertEquals(stderr, '')
    filter_dict, type_dict = json.loads(stdout)
    self.assertTrue('filter_dict' in locals())
    self.assertTrue('type_dict' in locals())
    self.assertNotEquals(filter_dict.get('writer8'), None)
    self.assertEquals(type_dict.get('writer8').get('Name'), 'writer8')
    self.assertNotEquals(filter_dict.get('writer8'), None)
    self.assertEquals(type_dict.get('writer8').get('PreferredFilter'), 'writer8')
    self.assertEquals(stderr, '')

  def testCallUnoMimemapperOnlyHostNameAndPort(self):
    """ Test call unomimemapper without uno_path and office_binary_path"""
    hostname, host = openoffice.getAddress()
    command = [path.join(self.office_binary_path, "python"),
            pkg_resources.resource_filename(self.package_namespace,
                                       "/helper/unomimemapper.py"),
            "--hostname=%s" % self.hostname,
            "--port=%s" % self.openoffice_port]
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    self.assertEquals(process.returncode, -3)
    self.assertEquals(stderr, '')
    filter_dict, type_dict = json.loads(stdout)
    self.assertTrue('filter_dict' in locals())
    self.assertTrue('type_dict' in locals())
    self.assertNotEquals(filter_dict.get('writer8'), None)
    self.assertEquals(type_dict.get('writer8').get('Name'), 'writer8')
    self.assertNotEquals(filter_dict.get('writer8'), None)
    self.assertEquals(type_dict.get('writer8').get('PreferredFilter'), 'writer8')
    self.assertEquals(stderr, '')

  def testWithoutOpenOffice(self):
    """Test when the openoffice is stopped"""
    error_msg = "couldn\'t connect to socket (Success)\n"
    hostname, host = openoffice.getAddress()
    openoffice.stop()
    python = path.join(self.office_binary_path, "python")
    command = [path.exists(python) and python or "python",
            pkg_resources.resource_filename(self.package_namespace,
                                            "/helper/unomimemapper.py"),
            "--uno_path=%s" % self.uno_path,
            "--office_binary_path=%s" % self.office_binary_path,
            "--hostname=%s" % self.hostname,
            "--port=%s" % self.openoffice_port]
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    self.assertEquals(process.returncode, -3)
    self.assertEquals(stdout, '')
    self.assertTrue(stderr.endswith(error_msg), stderr)
    openoffice.start()


