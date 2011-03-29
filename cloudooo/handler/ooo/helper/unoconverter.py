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
import helper_utils
from types import UnicodeType, InstanceType
from os import environ, putenv
from os.path import dirname, exists
from tempfile import mktemp
from base64 import decodestring, encodestring
from getopt import getopt, GetoptError

__doc__ = """

usage: unoconverter [options]

Options:
  -h, --help            this help screen

  --test                Test if the Openoffice works correctly

  --hostname=STRING     OpenOffice Instance address

  --port=STRING         OpenOffice Instance port

  --document_url=STRING_URL
                        URL of document to load in OpenOffice

  --office_binary_path=STRING_URL
                        Folder path were is the binary openoffice
  --uno_path=STRING_URL
                        Folter path were is the uno library
  --destination_format=STRING
                        extension to export the document
  --mimemapper=OBJECT_SERIALIZED
                        Mimemapper serialized. The object is passed using
                        json. IF this option is None, the object is
                        created
  --metadata=DICT_SERIALIZED
                        Dictionary with metadata
"""


class UnoConverter(object):
  """A module to easily work with OpenOffice.org."""

  def __init__(self, hostname, port, document_url, **kw):
    """ """
    self.hostname = hostname
    self.port = port
    self.document_url = document_url
    self.document_dir_path = dirname(document_url)
    self.source_format = kw.get('source_format')
    self.refresh = kw.get('refresh')
    self._setUpUnoEnvironment(kw.get("uno_path"),
                              kw.get("office_binary_path"))
    self._load()

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
    if exists(fundamentalrc_file) and \
       'URE_BOOTSTRAP' not in environ:
      putenv('URE_BOOTSTRAP', 'vnd.sun.star.pathname:%s' % fundamentalrc_file)

  def _createProperty(self, name, value):
    """Create property"""
    from com.sun.star.beans import PropertyValue
    property = PropertyValue()
    property.Name = name
    property.Value = value
    return property

  def _createSpecificProperty(self, filter_name):
    """Creates a property according to the filter"""
    import uno
    from com.sun.star.beans import PropertyValue
    if filter_name == "impress_html_Export":
      property = PropertyValue('FilterData', 0,
                        uno.Any('[]com.sun.star.beans.PropertyValue',
                        (PropertyValue('IsExportNotes', 0, True, 0),
                        PropertyValue('Format', 0, 2, 0),),), 0)
    elif filter_name == "impress_pdf_Export":
      property = PropertyValue('FilterData', 0,
                       uno.Any('[]com.sun.star.beans.PropertyValue',
                       (PropertyValue('ExportNotesPages', 0, True, 0),),), 0)
    elif filter_name in ("draw_html_Export", "HTML (StarCalc)"):
      property = PropertyValue('FilterData', 0,
                        uno.Any('[]com.sun.star.beans.PropertyValue',
                                (PropertyValue('Format', 0, 2, 0),),), 0)
    elif filter_name == "Text (encoded)":
      property = PropertyValue('FilterFlags', 0, 'UTF8,LF', 0)
    else:
      return []

    return [property, ]

  def _getFilterName(self, destination_format, type):
    for filter_tuple in mimemapper["filter_list"]:
      if destination_format == filter_tuple[0] and filter_tuple[1] == type:
        return filter_tuple[2]

  def _getPropertyToExport(self, destination_format=None):
    """Create the property according to the extension of the file."""
    if destination_format and self.document_loaded:
      filter_name = self._getFilterName(destination_format, self.document_type)
      property_list = []
      property = self._createProperty("Overwrite", True)
      property_list.append(property)
      property = self._createProperty("FilterName", filter_name)
      property_list.append(property)
      property_list.extend(self._createSpecificProperty(filter_name))
      return property_list
    else:
      return ()

  def _load(self):
    """Create one document with basic properties
    refresh argument tells to uno environment to
    replace dynamic properties of document before conversion
    """
    service_manager = helper_utils.getServiceManager(self.hostname, self.port)
    desktop = service_manager.createInstance("com.sun.star.frame.Desktop")
    uno_url = self.systemPathToFileUrl(self.document_url)
    uno_document = desktop.loadComponentFromURL(uno_url, "_blank", 0, ())
    if not uno_document:
      raise AttributeError("This document can not be loaded or is empty")
    if self.refresh:
      # Before converting to expected format, refresh dynamic
      # value inside document.
      dispatcher = service_manager.createInstance("com.sun.star.frame.DispatchHelper")
      for uno_command in ('UpdateFields', 'UpdateAll', 'UpdateInputFields',
                          'UpdateAllLinks', 'UpdateCharts',):
        dispatcher.executeDispatch(uno_document.getCurrentController().getFrame(),
                                   '.uno:%s' % uno_command, '', 0, ())
    module_manager = service_manager.createInstance("com.sun.star.frame.ModuleManager")
    self.document_type = module_manager.identify(uno_document)
    self.document_loaded = uno_document

  def systemPathToFileUrl(self, path):
    """Returns a path in uno library patterns"""
    from unohelper import systemPathToFileUrl
    return systemPathToFileUrl(path)

  def convert(self, output_format=None):
    """it converts a document to specific format"""
    if output_format in ("html", "htm", "xhtml"):
      destination_format = "impr.html"
    else:
      destination_format = output_format
    output_url = mktemp(suffix='.%s' % destination_format,
                        dir=self.document_dir_path)

    property_list = self._getPropertyToExport(output_format)
    try:
      self.document_loaded.storeToURL(self.systemPathToFileUrl(output_url),
         tuple(property_list))
    finally:
      self.document_loaded.dispose()
    return output_url

  def getMetadata(self):
    """Extract all metadata of the document"""
    metadata = {}
    document_info = self.document_loaded.getDocumentInfo()
    property_list = [prop.Name for prop in document_info.getPropertyValues() \
        if prop.Value]
    for property_name in iter(property_list):
      property = document_info.getPropertyValue(property_name)
      if type(property) == UnicodeType:
          metadata[property_name] = property
      elif type(property) == InstanceType:
        if property.typeName == 'com.sun.star.util.DateTime':
          datetime = "%s/%s/%s %s:%s:%s" % (property.Day, property.Month,
              property.Year, property.Hours, property.Minutes, property.Seconds)
          metadata[property_name] = datetime
    for number in range(document_info.getUserFieldCount()):
      field_value_str = document_info.getUserFieldValue(number)
      if field_value_str:
        fieldname = document_info.getUserFieldName(number)
        metadata[fieldname] = field_value_str
    service_manager = helper_utils.getServiceManager(self.hostname, self.port)
    type_detection = service_manager.createInstance("com.sun.star.document.TypeDetection")
    uno_file_access = service_manager.createInstance("com.sun.star.ucb.SimpleFileAccess")
    doc = uno_file_access.openFileRead(self.systemPathToFileUrl(self.document_url))
    input_stream = self._createProperty("InputStream", doc)
    open_new_view = self._createProperty("OpenNewView", True)
    filter_name = type_detection.queryTypeByDescriptor((input_stream,
                                                        open_new_view), True)[0]
    doc.closeInput()
    metadata['MIMEType'] = mimemapper["mimetype_by_filter_type"].get(filter_name)
    return metadata

  def setMetadata(self, metadata):
    """Returns a document with new metadata.

    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    doc_info = self.document_loaded.getDocumentInfo()
    prop_name_list = [prop.Name for prop in doc_info.getPropertyValues()]
    user_info_counter = 0
    for prop, value in metadata.iteritems():
      if prop in prop_name_list:
        doc_info.setPropertyValue(prop, value)
      else:
        max_index = doc_info.getUserFieldCount()
        for index in range(max_index):
          if doc_info.getUserFieldName(index).lower() == prop.lower():
            doc_info.setUserFieldValue(index, value)
            break
        else:
          doc_info.setUserFieldName(user_info_counter, prop)
          doc_info.setUserFieldValue(user_info_counter, value)
        user_info_counter += 1
    self.document_loaded.store()
    self.document_loaded.dispose()


def help():
  print >> sys.stderr, __doc__
  sys.exit(1)


def main():
  global mimemapper

  help_msg = "\nUse --help or -h"
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "h", ["help", "test",
      "convert", "getmetadata", "setmetadata",
      "uno_path=", "office_binary_path=",
      "hostname=", "port=", "source_format=",
      "document_url=", "destination_format=",
      "mimemapper=", "metadata=", "refresh=",
      "unomimemapper_bin="])
  except GetoptError, msg:
    msg = msg.msg + help_msg
    print >> sys.stderr, msg
    sys.exit(2)

  param_list = [tuple[0] for tuple in iter(opt_list)]

  try:
    import json
  except ImportError:
    import simplejson as json
  refresh = None
  for opt, arg in iter(opt_list):
    if opt in ('-h', '--help'):
      help()
    elif opt == '--hostname':
      hostname = arg
    elif opt == '--port':
      port = arg
    elif opt == '--document_url':
      document_url = arg
    elif opt == '--office_binary_path':
      environ['office_binary_path'] = arg
      office_binary_path = arg
    elif opt == '--uno_path':
      environ['uno_path'] = arg
      uno_path = arg
    elif opt == '--destination_format':
      destination_format = arg
    elif opt == '--source_format':
      source_format = arg
    elif opt == '--refresh':
      refresh = json.loads(arg)
    elif opt == '--metadata':
      arg = decodestring(arg)
      metadata = json.loads(arg)
    elif opt == '--mimemapper':
      mimemapper = json.loads(arg)

  kw = {}
  if "uno_path" in locals():
    kw['uno_path'] = uno_path

  if "office_binary_path" in locals():
    kw['office_binary_path'] = office_binary_path

  if 'source_format' in locals():
    kw['source_format'] = source_format
  if refresh:
    kw['refresh'] = refresh

  unoconverter = UnoConverter(hostname, port, document_url, **kw)
  if "--convert" in param_list and not '--getmetadata' in param_list \
      and 'destination_format' not in locals():
    output = unoconverter.convert()
  elif '--convert' in param_list and 'destination_format' in locals():
    output = unoconverter.convert(destination_format)
  elif '--getmetadata' in param_list and not '--convert' in param_list:
    metadata_dict = unoconverter.getMetadata()
    output = encodestring(json.dumps(metadata_dict))
  elif '--getmetadata' in param_list and '--convert' in param_list:
    document_url = unoconverter.convert()
    # Instanciate new UnoConverter instance with new url
    unoconverter = UnoConverter(hostname, port, document_url, **kw)
    metadata_dict = unoconverter.getMetadata()
    metadata_dict['document_url'] = document_url
    output = encodestring(json.dumps(metadata_dict))
  elif '--setmetadata' in param_list:
    unoconverter.setMetadata(metadata)
    output = document_url

  print output

if "__main__" == __name__:
  main()
