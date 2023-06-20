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

import sys
import json
import helper_util
from getopt import getopt, GetoptError


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


class UnoMimemapper:
  """ """

  def __init__(self, hostname, port, uno_path=None, office_binary_path=None):
    """ Receives hostname and port from openoffice and create a service manager"""
    self.service_manager = helper_util.getServiceManager(hostname, port,
                                                         uno_path,
                                                         office_binary_path)

  def _getElementNameByService(self, uno_service, ignore_name_list):
    """Returns an dict with elements."""
    name_list = uno_service.getElementNames()
    service_dict = {}
    for name in iter(name_list):
        element_dict = {}
        element_list = uno_service.getByName(name)
        for obj in iter(element_list):
            if obj.Name in ignore_name_list:
              continue
            if not isinstance(obj.Value, (bool, int, str, tuple)):
              continue
            element_dict[obj.Name] = obj.Value
            service_dict[name] = element_dict

    return service_dict

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
  sys.stderr.write(__doc__)
  sys.exit(1)


def main():
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "h", ["help",
      "uno_path=", "office_binary_path=",
      "hostname=", "port="])
  except GetoptError as msg:
    msg = msg.msg + "\nUse --help or -h\n"
    sys.stderr.write(msg)
    sys.exit(2)

  if not opt_list:
    help()

  port = hostname = uno_path = office_binary_path = None
  for opt, arg in opt_list:
    if opt in ("-h", "--help"):
      help()
    if opt == "--uno_path":
      uno_path = arg
    elif opt == "--office_binary_path":
      office_binary_path = arg
    elif opt == '--hostname':
      hostname = arg
    elif opt == "--port":
      port = arg

  mimemapper = UnoMimemapper(hostname, port, uno_path, office_binary_path)
  filter_dict = mimemapper.getFilterDict()
  type_dict = mimemapper.getTypeDict()

  sys.stdout.write(json.dumps((filter_dict, type_dict),
                              sort_keys=True, indent=2, separators=(',', ':')))

if "__main__" == __name__:
  main()
