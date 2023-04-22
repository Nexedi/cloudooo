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

import json
import pkg_resources
from cloudooo.handler.ooo.application.openoffice import openoffice
from subprocess import Popen, PIPE
from os import environ, path
from cloudooo.tests.handlerTestCase import HandlerTestCase

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
    stdout, stderr = Popen(command,
                           stdout=PIPE,
                           stderr=PIPE,
                           text=True).communicate()
    self.assertEqual(stderr, '')
    filter_dict, type_dict = json.loads(stdout)
    self.assertNotEqual(filter_dict.get('writer8'), None)
    self.assertEqual(type_dict.get('writer8').get('Name'), 'writer8')
    self.assertNotEqual(filter_dict.get('writer8'), None)
    self.assertEqual(type_dict.get('writer8').get('PreferredFilter'), 'writer8')
    self.assertEqual(stderr, '')

  def testCallUnoMimemapperOnlyHostNameAndPort(self):
    """ Test call unomimemapper without uno_path and office_binary_path"""
    hostname, host = openoffice.getAddress()
    command = [path.join(self.office_binary_path, "python"),
            pkg_resources.resource_filename(self.package_namespace,
                                       "/helper/unomimemapper.py"),
            "--hostname=%s" % self.hostname,
            "--port=%s" % self.openoffice_port]
    stdout, stderr = Popen(command,
                           stdout=PIPE,
                           stderr=PIPE,
                           text=True).communicate()
    self.assertEqual(stderr, '')
    filter_dict, type_dict = json.loads(stdout)
    self.assertNotEqual(filter_dict.get('writer8'), None)
    self.assertEqual(type_dict.get('writer8').get('Name'), 'writer8')
    self.assertNotEqual(filter_dict.get('writer8'), None)
    self.assertEqual(type_dict.get('writer8').get('PreferredFilter'), 'writer8')
    self.assertEqual(stderr, '')

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
    # due to a5157949fb5fc9e0c4b0b204f0e737c15498cf38 
    # cloudooo will retry 10 times before raising thus take this into account
    for i in range(10):
      stdout, stderr = Popen(command,
                             stdout=PIPE,
                             stderr=PIPE,
                             text=True).communicate()
    self.assertEqual(stdout, '')
    self.assertIn(error_msg, stderr)
    openoffice.start()


