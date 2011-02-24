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


import unittest
import sys
from os import environ, path, mkdir, putenv
from ConfigParser import ConfigParser
from cloudooo.handler.ooo.application.openoffice import openoffice
from cloudooo.handler.ooo.mimemapper import mimemapper

config = ConfigParser()


def make_suite(test_case):
  """Function is used to run all tests together"""
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(test_case))
  return suite


def check_folder(working_path, tmp_dir_path):
  if not path.exists(working_path):
    mkdir(working_path)
  if not path.exists(tmp_dir_path):
    mkdir(tmp_dir_path)


def startFakeEnvironment(start_openoffice=True, conf_path=None):
  """Create a fake environment"""

  config.read(conf_path)
  uno_path = config.get("app:main", "uno_path")
  working_path = config.get("app:main", "working_path")
  hostname = config.get("server:main", "host")
  openoffice_port = int(config.get("app:main", "openoffice_port"))
  office_binary_path = config.get("app:main", "office_binary_path")
  tmp_dir = path.join(working_path, 'tmp')
  check_folder(working_path, tmp_dir)
  if not environ.get('uno_path'):
    environ['uno_path'] = uno_path
  office_binary_path = config.get("app:main", "office_binary_path")
  if not environ.get('office_binary_path'):
    environ['office_binary_path'] = office_binary_path

  if uno_path not in sys.path:
    sys.path.append(uno_path)

  fundamentalrc_file = '%s/fundamentalrc' % office_binary_path
  if path.exists(fundamentalrc_file) and \
      'URE_BOOTSTRAP' not in environ:
    putenv('URE_BOOTSTRAP', 'vnd.sun.star.pathname:%s' % fundamentalrc_file)

  if start_openoffice:
    default_language = config.get('app:main',
                                  'openoffice_user_interface_language', False,
                                  {'openoffice_user_interface_language': 'en'})
    openoffice.loadSettings(hostname,
                            openoffice_port,
                            working_path,
                            office_binary_path,
                            uno_path,
                            default_language)
    openoffice.start()
    openoffice.acquire()
    hostname, port = openoffice.getAddress()
    kw = dict(uno_path=config.get("app:main", "uno_path"),
              office_binary_path=config.get("app:main", "office_binary_path"))
    if not mimemapper.isLoaded():
        mimemapper.loadFilterList(hostname, port, **kw)
    openoffice.release()
    return openoffice


def stopFakeEnvironment(stop_openoffice=True):
  """Stop Openoffice """
  if stop_openoffice:
    openoffice.stop()
  return True


class HandlerTestCase(unittest.TestCase):
  """Test Case to load cloudooo conf."""

  def setUp(self):
    """Creates a environment to run the tests. Is called always before the
    tests."""
    server_cloudooo_conf = environ.get("server_cloudooo_conf", None)
    if server_cloudooo_conf is not None:
      config.read(server_cloudooo_conf)
    self.hostname = config.get("server:main", "host")
    self.cloudooo_port = config.get("server:main", "port")
    self.openoffice_port = config.get("app:main", "openoffice_port")
    self.office_binary_path = config.get("app:main", "office_binary_path")
    self.python_path = sys.executable
    self.env_path = config.get("app:main", "env-path")
    self.working_path = config.get("app:main", "working_path")
    self.tmp_url = path.join(self.working_path, "tmp")
    check_folder(self.working_path, self.tmp_url)
    self.uno_path = config.get("app:main", "uno_path")
    self.afterSetUp()

  def afterSetUp(self):
    """ """
