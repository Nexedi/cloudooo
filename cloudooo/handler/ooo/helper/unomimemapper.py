#!/usr/bin/env python
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
try:
  import json
except ImportError:
  import simplejson as json
import helper_utils
from os import environ, path, putenv
from getopt import getopt, GetoptError
from types import InstanceType

__doc__ = """

usage: unomimemapper [options]

Options:
  -h, --help            this help screen
  --hostname=STRING     OpenOffice Instance address

  --port=STRING         OpenOffice Instance port

  --office_binary_path=STRING_URL
                        Folder path were is the binary openoffice
  --uno_path=STRING_URL
                        Folter path were is the uno library
"""


class UnoMimemapper(object):
  """ """

  def __init__(self, hostname, port, **kw):
    """ Receives hostname and port from openoffice and create a service manager"""
    self._setUpUnoEnvironment(kw.get("uno_path"),
                              kw.get("office_binary_path"))
    self.service_manager = helper_utils.getServiceManager(hostname, port)

  def _getElementNameByService(self, uno_service, ignore_name_list=[]):
    """Returns an dict with elements."""
    name_list = uno_service.getElementNames()
    service_dict = {}
    for name in iter(name_list):
        element_dict = {}
        element_list = uno_service.getByName(name)
        for obj in iter(element_list):
            if obj.Name in ignore_name_list:
              continue
            elif type(obj.Value) == InstanceType:
              continue
            element_dict[obj.Name] = obj.Value
            service_dict[name] = element_dict

    return service_dict

  def _setUpUnoEnvironment(self, uno_path=None, office_binary_path=None):
    """Set up the environment to use the uno library and connect with the
    openoffice by socket"""
    if uno_path is not None:
      environ['uno_path'] = uno_path
    else:
      uno_path = environ.get('uno_path')

    if office_binary_path is not None:
      environ['office_binary_path'] = office_binary_path
    else:
      office_binary_path = environ.get('office_binary_path')

    # Add in sys.path the path of pyuno
    if uno_path not in sys.path:
      sys.path.append(uno_path)
    fundamentalrc_file = '%s/fundamentalrc' % office_binary_path
    if path.exists(fundamentalrc_file) and \
       not environ.has_key('URE_BOOTSTRAP'):
      putenv('URE_BOOTSTRAP','vnd.sun.star.pathname:%s' % fundamentalrc_file)

  def getFilterDict(self):
    """Return all filters and your properties"""
    filter_service = self.service_manager.createInstance("com.sun.star.document.FilterFactory")
    filter_dict = self._getElementNameByService(filter_service, ["UINames", "UserData"])
    return filter_dict

  def getTypeDict(self):
    """Return all types and your properties"""
    type_service = self.service_manager.createInstance("com.sun.star.document.TypeDetection")
    type_dict = self._getElementNameByService(type_service, ["UINames", "URLPattern"])
    return type_dict


def help():
  print >> sys.stderr, __doc__
  sys.exit(1)


def main():
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "h", ["help",
      "uno_path=", "office_binary_path=",
      "hostname=", "port="])
  except GetoptError, msg:
    msg = msg.msg + "\nUse --help or -h"
    print >> sys.stderr, msg
    sys.exit(2)

  if not opt_list:
    help()

  for opt, arg in opt_list:
    if opt in ("-h", "--help"):
      help()
    if opt == "--uno_path":
      environ['uno_path'] = arg
    elif opt == "--office_binary_path":
      environ['office_binary_path'] = arg
    elif opt == '--hostname':
      hostname = arg
    elif opt == "--port":
      port = arg

  mimemapper = UnoMimemapper(hostname, port, **dict(environ))
  filter_dict = mimemapper.getFilterDict()
  type_dict = mimemapper.getTypeDict()

  print json.dumps((filter_dict, type_dict))

if "__main__" == __name__:
  main()
