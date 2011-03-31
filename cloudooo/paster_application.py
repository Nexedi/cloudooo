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

from os import path, mkdir
import os
import sys
from cloudooo.wsgixmlrpcapplication import WSGIXMLRPCApplication
from cloudooo.utils import utils


def application(global_config, **local_config):
  """Method to load all configuration of cloudooo and start the application.
  To start the application a number of params are required:
  Keyword arguments:
  debug_mode -- Mode as the application prints the messages.
      e.g debug_mode=logging.DEBUG
  working_path -- Full path to create the environment of the processes.
      e.g working_path='/var/run/cloudooo'
  application_hostname -- Sets the host to Openoffice.
  office_binary_path -- Folder where soffice.bin is installed.
      e.g office_binary_path='/opt/libreoffice/program'
  uno_path -- Folder where UNO library is installed.
      e.g uno_path='/opt/libreoffice/basis-link/program/'
  """
  prefix = 'env-'
  environment_dict = {}
  for parameter_name, value in local_config.iteritems():
    if parameter_name.startswith(prefix):
      value = value or ''
      variable_name = parameter_name[len(prefix):]
      if variable_name == 'PATH':
        # merge only for PATH
        current_value = os.environ.get(variable_name, '')
        if current_value:
          value = '%s:%s' % (value, current_value)
      environment_dict[variable_name] = value

  local_config['environment_dict'] = environment_dict

  gc.enable()
  debug_mode = utils.convertStringToBool(local_config.get('debug_mode'))
  utils.configureLogger(debug_mode=debug_mode)
  # path of directory to run cloudooo
  working_path = local_config.get('working_path')
  if not path.exists(working_path):
    mkdir(working_path)
  # directory to create temporary files
  cloudooo_path_tmp_dir = path.join(working_path, 'tmp')
  if not path.exists(cloudooo_path_tmp_dir):
    mkdir(cloudooo_path_tmp_dir)

  utils.loadMimetypeList()

  mimetype_registry = local_config.get("mimetype_registry", "")
  local_config["mimetype_registry"] = handler_mapping_list = \
                                    filter(None, mimetype_registry.split("\n"))
  handler_dict = {}
  for line in handler_mapping_list:
    input_mimetype, output_mimetype, handler = line.strip().split()
    if handler not in handler_dict:
      import_path = "cloudooo.handler.%s.handler" % handler
      # Import Errors are not catched, check your configuration file
      module = __import__(import_path, globals(), locals(), [''])
      # Call the bootstraping method
      getattr(module, 'bootstrapHandler', lambda x: None)(local_config)
      handler_dict[handler] = module.Handler

  local_config['handler_dict'] = handler_dict
  local_config["env"] = environment_dict
  from manager import Manager
  cloudooo_manager = Manager(cloudooo_path_tmp_dir, **local_config)
  return WSGIXMLRPCApplication(instance=cloudooo_manager)
