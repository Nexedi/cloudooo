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

import gc
from signal import signal, SIGHUP
from os import path, mkdir

import cloudooo.handler.ooo.monitor as monitor
from cloudooo.handler.ooo.application.openoffice import openoffice
from cloudooo.handler.ooo.application.xvfb import xvfb
from cloudooo.wsgixmlrpcapplication import WSGIXMLRPCApplication
from cloudooo.utils.utils import convertStringToBool, configureLogger
from cloudooo.handler.ooo.mimemapper import mimemapper

def stopProcesses(signum, frame):
  monitor.stop()
  xvfb.stop()
  openoffice.stop()


def application(global_config, **local_config):
  """Method to load all configuration of cloudooo and start the application.
  To start the application a number of params are required:
  Keyword arguments:
  debug_mode -- Mode as the application prints the messages.
      e.g debug_mode=logging.DEBUG
  working_path -- Full path to create the environment of the processes.
      e.g working_path='/var/run/cloudooo'
  virtual_display_port -- Port to start the Xvfb.
  virtual_display_id -- Sets the display.
      e.g virtual_display_id='99'
  application_hostname -- Sets the host to Xvfb and Openoffice.
  virtual_screen -- Use to define the screen to Xvfb
      e.g virtual_screen='0'
  office_binary_path -- Full Path of the OOo executable.
      e.g office_binary_path='/opt/openoffice.org3/program'
  uno_path -- Full path to pyuno library.
      e.g uno_path='/opt/openoffice.org/program'
  """
  gc.enable()
  debug_mode = convertStringToBool(local_config.get('debug_mode'))
  configureLogger(debug_mode=debug_mode)
  # path of directory to run cloudooo
  working_path = local_config.get('working_path')
  if not path.exists(working_path):
    mkdir(working_path)
  # directory to create temporary files
  cloudooo_path_tmp_dir = path.join(working_path, 'tmp')
  if not path.exists(cloudooo_path_tmp_dir):
    mkdir(cloudooo_path_tmp_dir)
  # The Xvfb will run in the same local of the OpenOffice
  application_hostname = local_config.get('application_hostname')
  openoffice_port = int(local_config.get('openoffice_port'))
  # Before start Xvfb, first loads the configuration
  xvfb.loadSettings(application_hostname,
                    int(local_config.get('virtual_display_port')),
                    working_path,
                    local_config.get('virtual_display_id'),
                    virtual_screen=local_config.get('virtual_screen'),
                    start_timeout=local_config.get('start_timeout'))
  xvfb.start()

  # Loading Configuration to start OOo Instance and control it
  openoffice.loadSettings(application_hostname,
                          openoffice_port,
                          working_path,
                          local_config.get('virtual_display_id'),
                          local_config.get('office_binary_path'),
                          local_config.get('uno_path'),
                          local_config.get('openoffice_user_interface_language',
                                           'en'),
                          )
  openoffice.start()

  monitor.load(local_config)
  timeout_response = int(local_config.get('timeout_response'))
  kw = dict(uno_path=local_config.get('uno_path'),
           office_binary_path=local_config.get('office_binary_path'),
           timeout=timeout_response)

  # Signal to stop all processes
  signal(SIGHUP, stopProcesses)

  # Load all filters
  openoffice.acquire()
  mimemapper.loadFilterList(application_hostname,
                            openoffice_port, **kw)
  openoffice.release()
  from manager import Manager
  cloudooo_manager = Manager(cloudooo_path_tmp_dir, **kw)
  return WSGIXMLRPCApplication(instance=cloudooo_manager)
