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

from os import environ, putenv
from sys import path
from os.path import exists

def setUpUnoEnvironment(uno_path=None, office_bin_path=None):
  """Set up the environment to use the uno library and connect with the
  openoffice by socket""" 
  if uno_path is not None:
    environ['uno_path'] = uno_path
  else:
    uno_path = environ.get('uno_path')

  if office_bin_path is not None:
    environ['office_bin_path'] = office_bin_path
  else:
    office_bin_path = environ.get('office_bin_path')

  # Add in sys.path the path of pyuno
  if uno_path not in path:
    path.append(uno_path)
  fundamentalrc_file = '%s/fundamentalrc' % office_bin_path
  if exists(fundamentalrc_file) and \
       not environ.has_key('URE_BOOTSTRAP'):
    putenv('URE_BOOTSTRAP','vnd.sun.star.pathname:%s' % fundamentalrc_file)

def createProperty(name, value):
  """Create property"""
  setUpUnoEnvironment()
  from com.sun.star.beans import PropertyValue
  property = PropertyValue()
  property.Name = name
  property.Value = value
  return property

# XXX - method duplicated
def createHTMLProperty():
  """Returns a property to create all images in png format"""
  setUpUnoEnvironment()
  import uno
  from com.sun.star.beans import PropertyValue

  property = PropertyValue('FilterData', 0, 
      uno.Any('[]com.sun.star.beans.PropertyValue',
        (PropertyValue('IsExportNotes', 0, True, 0),
          PropertyValue('Format', 0, 2, 0),),), 0) # PNG format
  return property

def getServiceManager(host, port):
  """Get the ServiceManager from the running OpenOffice.org."""
  setUpUnoEnvironment()
  import uno
  # Get the uno component context from the PyUNO runtime
  uno_context = uno.getComponentContext()
  # Create the UnoUrlResolver on the Python side.
  url_resolver = "com.sun.star.bridge.UnoUrlResolver"
  resolver = uno_context.ServiceManager.createInstanceWithContext(url_resolver,
      uno_context)
  # Connect to the running OpenOffice.org and get its
  # context.
  uno_connection = resolver.resolve("uno:socket,host=%s,port=%s;urp;StarOffice.ComponentContext" % (host, port))
  # Get the ServiceManager object
  return uno_connection.ServiceManager

def systemPathToFileUrl(path):
  """Returns a path in uno library patterns"""
  setUpUnoEnvironment()
  from unohelper import systemPathToFileUrl
  
  return systemPathToFileUrl(path)
