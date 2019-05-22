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
import csv
import codecs
import helper_util
from os.path import dirname, splitext
from tempfile import mktemp
from base64 import decodestring, encodestring
from getopt import getopt, GetoptError

try:
  basestring
except NameError:
  basestring = str

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

  def __init__(self, service_manager, document_url, source_format, refresh):
    """ """
    self.service_manager = service_manager
    self.document_url = document_url
    self.document_dir_path = dirname(document_url)
    self.source_format = source_format
    self.refresh = refresh
    self._load()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    if traceback:
      sys.stderr.write(str(traceback))
    self.document_loaded.close(True)

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
                        PropertyValue('PublishMode', 0, 0, 0),
                        PropertyValue('Width', 0, 640, 0),
                        PropertyValue('Format', 0, 2, 0),),), 0)
    elif filter_name == "impress_pdf_Export":
      property = PropertyValue('FilterData', 0,
                       uno.Any('[]com.sun.star.beans.PropertyValue',
                       (PropertyValue('ExportNotesPages', 0, True, 0),
                       PropertyValue('SelectPdfVersion', 0, 1, 0),),), 0)
    elif "pdf_Export" in filter_name :
      property = PropertyValue('FilterData', 0,
                       uno.Any('[]com.sun.star.beans.PropertyValue',
                       (PropertyValue('SelectPdfVersion', 0, 1, 0),),), 0)
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

  def _getPropertyToImport(self, source_url):
    """Create the property for import filter, according to the extension of the file."""
    _, extension = splitext(source_url)
    if extension == '.csv':
      # https://wiki.openoffice.org/wiki/Documentation/DevGuide/Spreadsheets/Filter_Options

      # Try to sniff the csv delimiter
      with codecs.open(source_url, 'rb', 'utf-8', errors="ignore") as csvfile:
        try:
          dialect = csv.Sniffer().sniff(csvfile.read(1024))
          delimiter = ord(dialect.delimiter)
        except csv.Error:
          delimiter = ord(',')

      return (
        self._createProperty("FilterName", "Text - txt - csv (StarCalc)"),
        self._createProperty("FilterOptions", "{delimiter},34,UTF-8".format(**locals())), )

    return ()

  def _load(self):
    """Create one document with basic properties
    refresh argument tells to uno environment to
    replace dynamic properties of document before conversion
    """
    service_manager = self.service_manager
    desktop = service_manager.createInstance("com.sun.star.frame.Desktop")
    uno_url = self.systemPathToFileUrl(self.document_url)
    uno_document = desktop.loadComponentFromURL(
        uno_url,
        "_blank",
        0,
        self._getPropertyToImport(self.document_url))
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
    self.document_loaded.storeToURL(self.systemPathToFileUrl(output_url),
       tuple(property_list))
    return output_url

  def getMetadata(self):
    """Extract all metadata of the document"""
    metadata = {}
    document_properties = self.document_loaded.getDocumentProperties()
    user_defined_properties = document_properties.getUserDefinedProperties()
    for container in [document_properties, user_defined_properties]:
      for property_name in dir(container):
        if property_name in ('SupportedServiceNames',):
          continue
        property_value = getattr(container, property_name, '')
        if property_value:
          if isinstance(property_value, basestring):
            metadata[property_name] = property_value
          elif isinstance(property_value, tuple) and isinstance(property_value[0], basestring):
            metadata[property_name] = property_value
          else:
            try:
              if property_value.typeName == 'com.sun.star.util.DateTime':
                # It is a local time and we have no timezone information.
                datetime = "%02d/%02d/%04d %02d:%02d:%02d" % (property_value.Day, property_value.Month,
                    property_value.Year, property_value.Hours, property_value.Minutes, property_value.Seconds)
                metadata[property_name] = datetime
            except AttributeError:
              pass

    service_manager = self.service_manager
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
    document_properties = self.document_loaded.getDocumentProperties()
    user_defined_properties = document_properties.getUserDefinedProperties()
    new_properties = []
    for prop, value in metadata.items():
      for container in [document_properties, user_defined_properties]:
        current_value = getattr(container, prop, None)
        if current_value is not None:
          if isinstance(current_value, tuple):
            if isinstance(value, list):
              value = tuple(value)
            elif isinstance(value, basestring):
              # BBB: old ERP5 code sends Keywords as a string
              # separated by a whitespace.
              value = tuple(value.split(' '))
          if isinstance(value, type(current_value)):
            setattr(container, prop, value)
          break
      else:
        new_properties.append([prop, value])
    for prop, value in new_properties:
      if isinstance(value, basestring):
        user_defined_properties.addProperty(prop, 0, '')
        user_defined_properties.setPropertyValue(prop, value)
    self.document_loaded.store()


def help():
  sys.stderr.write(__doc__)
  sys.exit(1)


def main():
  global mimemapper

  help_msg = "\nUse --help or -h\n"
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "h", ["help", "test",
      "convert", "getmetadata", "setmetadata",
      "uno_path=", "office_binary_path=",
      "connection=", "source_format=",
      "document_url=", "destination_format=",
      "mimemapper=", "metadata=", "refresh=",
      "unomimemapper_bin="])
  except GetoptError as msg:
    msg = msg.msg + help_msg
    sys.stderr.write(msg)
    sys.exit(2)

  param_list = [tuple[0] for tuple in iter(opt_list)]

  try:
    import json
  except ImportError:
    import simplejson as json
  connection = document_url = office_binary_path = uno_path =\
  destination_format = source_format = refresh = metadata = mimemapper = None
  for opt, arg in iter(opt_list):
    if opt in ('-h', '--help'):
      help()
    elif opt == '--connection':
      connection = arg
    elif opt == '--document_url':
      document_url = arg
    elif opt == '--office_binary_path':
      office_binary_path = arg
    elif opt == '--uno_path':
      uno_path = arg
    elif opt == '--destination_format':
      destination_format = arg
    elif opt == '--source_format':
      source_format = arg
    elif opt == '--refresh':
      refresh = json.loads(arg)
    elif opt == '--metadata':
      arg = decodestring(arg.encode('ascii')).decode('utf-8')
      metadata = json.loads(arg)
    elif opt == '--mimemapper':
      mimemapper = json.loads(arg)

  service_manager = helper_util.getServiceManager(connection,
                                                  uno_path, office_binary_path)
  if '--getmetadata' in param_list and '--convert' in param_list:
    with UnoConverter(service_manager, document_url,  source_format, refresh) as unoconverter:
      document_url = unoconverter.convert()
      # Instanciate new UnoConverter instance with new url
    with UnoConverter(service_manager, document_url, source_format, refresh) as unoconverter:
      metadata_dict = unoconverter.getMetadata()
      metadata_dict['document_url'] = document_url
      output = encodestring(json.dumps(metadata_dict).encode('utf-8')).decode('utf-8')
  else:
    with UnoConverter(service_manager, document_url,  source_format, refresh) as unoconverter:
      if "--convert" in param_list and not destination_format:
        output = unoconverter.convert()
      elif '--convert' in param_list and destination_format:
        output = unoconverter.convert(destination_format)
      elif '--getmetadata' in param_list:
        metadata_dict = unoconverter.getMetadata()
        output = encodestring(json.dumps(metadata_dict).encode('utf-8')).decode('utf-8')
      elif '--setmetadata' in param_list:
        unoconverter.setMetadata(metadata)
        output = document_url

  sys.stdout.write(output)

if "__main__" == __name__:
  helper_util.exitOverAbort(main)