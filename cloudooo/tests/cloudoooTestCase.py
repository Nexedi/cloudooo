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

import unittest
from sys import path
from ConfigParser import ConfigParser
from os.path import join, exists, dirname
from os import environ, putenv
from cloudooo.application.xvfb import xvfb
from cloudooo.application.openoffice import openoffice
from cloudooo.utils import waitStartDaemon
from cloudooo.mimemapper import mimemapper

config = ConfigParser()
testcase_path = dirname(__file__)

def make_suite(test_case):
  """Function is used to run all tests together"""
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(test_case))
  return suite

def loadConfig(path=None):
  conf_path = path or join(testcase_path, "..", "samples/cloudooo.conf")
  config.read(conf_path)

def startFakeEnvironment(start_openoffice=True, conf_path=None):
  """Create a fake environment"""
  loadConfig(conf_path)
  uno_path = config.get("app:main", "uno_path")
  path_dir_run_cloudooo = config.get("app:main", "path_dir_run_cloudooo")
  virtual_display_id = int(config.get("app:main", "virtual_display_id"))
  virtual_display_port_int = int(config.get("app:main", "virtual_display_port"))
  hostname = config.get("server:main", "host")
  openoffice_port = int(config.get("app:main", "openoffice_port"))
  office_bin_path = config.get("app:main", "office_bin_path")
  if not environ.get('uno_path'):
    environ['uno_path'] = uno_path
  
  office_bin_path = config.get("app:main", "office_bin_path")
  if not environ.get('office_bin_path'):
    environ['office_bin_path'] = office_bin_path
  
  if not uno_path in path:
      path.append(uno_path)
  
  fundamentalrc_file = '%s/fundamentalrc' % office_bin_path
  if exists(fundamentalrc_file) and \
      not environ.has_key('URE_BOOTSTRAP'):
    putenv('URE_BOOTSTRAP','vnd.sun.star.pathname:%s' % fundamentalrc_file)

  xvfb.loadSettings(hostname,
                  virtual_display_port_int,
                  path_dir_run_cloudooo,
                  virtual_display_id,
                  virtual_screen='1')
  xvfb.start()
  waitStartDaemon(xvfb, 10)
  if start_openoffice:
    openoffice.loadSettings(hostname,
                            openoffice_port, 
                            path_dir_run_cloudooo,
                            virtual_display_id,
                            office_bin_path, 
                            uno_path)
    openoffice.start()
    openoffice.acquire()
    hostname, port = openoffice.getAddress()
    kw = dict(python_path=config.get("app:main", "python_path"),
              unomimemapper_bin=config.get("app:main", "unomimemapper_bin"),
              uno_path=config.get("app:main", "uno_path"),
              office_bin_path=config.get("app:main", "office_bin_path"))
    if not mimemapper.isLoaded():
        mimemapper.loadFilterList(hostname, port, **kw)
    openoffice.release()
    return openoffice, xvfb
  
  return xvfb

def stopFakeEnvironment(stop_openoffice=True):
  """Stop Openoffice and Xvfb """
  if stop_openoffice:
    openoffice.stop()
  xvfb.stop()
  return True

class cloudoooTestCase(unittest.TestCase):
  """Test Case to load cloudooo conf."""
  
  def setUp(self):
    """Creates a environment to run the tests. Is called always before the
    tests."""
    loadConfig()
    self.hostname = config.get("server:main", "host")
    self.cloudooo_port = config.get("server:main", "port")
    self.openoffice_port = config.get("app:main", "openoffice_port")
    self.office_bin_path = config.get("app:main", "office_bin_path")
    self.path_dir_run_cloudooo = config.get("app:main", "path_dir_run_cloudooo")
    self.tmp_url = join(self.path_dir_run_cloudooo, "tmp") 
    self.uno_path = config.get("app:main", "uno_path")
    self.unomimemapper_bin = config.get("app:main", "unomimemapper_bin")
    self.unoconverter_bin = config.get("app:main", "unoconverter_bin")
    self.python_path = config.get("app:main", "python_path")
    self.virtual_display_id = config.get("app:main", "virtual_display_id")
    self.virtual_display_port_int = config.get("app:main", "virtual_display_port")
    self.afterSetUp()

  def afterSetUp(self):
    """ """
