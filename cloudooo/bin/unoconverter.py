#!/usr/bin/env python
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

import sys
import jsonpickle
from types import UnicodeType, InstanceType
from os import environ
from os.path import dirname
from tempfile import mktemp
from getopt import getopt, GetoptError
from cloudooo import ooolib
from cloudooo.utils import usage

__doc__ = """

usage: unoconverter [options]

Options:
  -h, --help            this help screen
  
  --test                Test if the Openoffice works correctly
  
  --hostname=STRING     OpenOffice Instance address
  
  --port=STRING         OpenOffice Instance port
  
  --document_url=STRING_URL 
                        URL of document to load in OpenOffice
  
  --office_bin_path=STRING_URL
                        Folder path were is the binary openoffice
  --uno_path=STRING_URL
                        Folter path were is the uno library
  --destination_format=STRING
                        extension to export the document
  --mimemapper=OBJECT_SERIALIZED
                        Mimemapper serialized. The object is passed using
                        jsonpickle. IF this option is None, the object is
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
    self._load()

  def _getPropertyToExport(self, destination_format=None):
    """Create the property according to the extension of the file."""
    if destination_format and self.document_loaded:
      doc_type_list = mimemapper._doc_type_list_by_extension.get(destination_format)
      if self.document_type not in doc_type_list:
        raise AttributeError, \
                        "This Document can not be converted for this format"
      type = self.document_type
      filter_name = mimemapper.getFilterName(destination_format, type)
      property_list = []
      property = ooolib.createProperty("Overwrite", True)
      property_list.append(property)
      property = ooolib.createProperty("FilterName", filter_name)
      property_list.append(property)
      if "htm" in destination_format:
        # XXX - condition to obtain a property that returns all images in png
        # format
        property_list.append(ooolib.createHTMLProperty())
      return property_list
    else:
      return ()

  def _load(self):
    """Create one document with basic properties"""
    service_manager = ooolib.getServiceManager(self.hostname, self.port)
    desktop = service_manager.createInstance("com.sun.star.frame.Desktop")
    uno_url = ooolib.systemPathToFileUrl(self.document_url)
    uno_document = desktop.loadComponentFromURL(uno_url, "_blank", 0, ())
    module_manager = service_manager.createInstance("com.sun.star.frame.ModuleManager")
    if not uno_document:
      raise AttributeError, "This document can not be loaded or is empty"
    self.document_type = module_manager.identify(uno_document)
    self.document_loaded = uno_document
 
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
      self.document_loaded.storeToURL(ooolib.systemPathToFileUrl(output_url),
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
    service_manager = ooolib.getServiceManager(self.hostname, self.port)
    uno_file_access = service_manager.createInstance("com.sun.star.ucb.SimpleFileAccess")
    doc = uno_file_access.openFileRead(ooolib.systemPathToFileUrl(self.document_url))
    property_list = []
    property = ooolib.createProperty("InputStream", doc)
    property_list.append(property)
    type_detection = service_manager.createInstance("com.sun.star.document.TypeDetection")
    filter_name = type_detection.queryTypeByDescriptor(tuple(property_list), \
        True)[0]
    doc.closeInput()
    metadata['MIMEType'] = mimemapper.getMimetypeByFilterType(filter_name)
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
  usage(sys.stderr, __doc__)
  sys.exit(1)

def main():
  global mimemapper

  help_msg = "\nUse --help or -h"
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "h", ["help", "test",
      "convert", "getmetadata", "setmetadata",
      "uno_path=", "office_bin_path=", 
      "hostname=", "port=", "source_format=",
      "document_url=", "destination_format=", 
      "mimemapper=", "metadata=",
      "unomimemapper_bin=", "python_path="])
  except GetoptError, msg:
    msg = msg.msg + help_msg
    usage(sys.stderr, msg)
    sys.exit(2)
  
  param_list = [tuple[0] for tuple in opt_list]

  for opt, arg in opt_list:
    if opt in ('-h', '--help'):
      help()
    elif opt == '--hostname':
      hostname = arg
    elif opt == '--port':
      port = arg
    elif opt == '--document_url':
      document_url = arg
    elif opt == '--office_bin_path':
      environ['office_bin_path'] = arg
      office_bin_path = arg
    elif opt == '--uno_path':
      environ['uno_path'] = arg
      uno_path = arg
    elif opt == '--destination_format':
      destination_format = arg
    elif opt == '--source_format':
      source_format = arg
    elif opt == '--metadata':
      metadata = jsonpickle.decode(arg)
    elif opt == '--mimemapper':
      mimemapper = jsonpickle.decode(arg)
    elif opt == '--unomimemapper_bin':
      unomimemapper_bin = arg
    elif opt == '--python_path':
      python_path = arg
   
  kw = {}
  
  if "mimemapper" not in globals() and "--setmetadata" not in param_list:
    from cloudooo.mimemapper import mimemapper
    if "uno_path" in locals():
      kw['uno_path'] = uno_path

    if "office_bin_path" in locals():
      kw['office_bin_path'] = office_bin_path
    
    if "unomimemapper_bin" in locals():
      kw['unomimemapper_bin'] = unomimemapper_bin

    if "python_path" in locals():
      kw['python_path'] = python_path

    mimemapper.loadFilterList(hostname=hostname, port=port, **kw)
  
  kw.clear()
  if 'source_format' in locals():
    kw['source_format'] = source_format

  unoconverter = UnoConverter(hostname, port, document_url, **kw)
  if "--test" in param_list:
    output = unoconverter.convert("pdf")
  if "--convert" in param_list and not '--getmetadata' in param_list \
      and 'destination_format' not in locals():
    output = unoconverter.convert()
  elif '--convert' in param_list and 'destination_format' in locals():
    output = unoconverter.convert(destination_format)
  elif '--getmetadata' in param_list and not '--convert' in param_list:
    output = unoconverter.getMetadata()
  elif '--getmetadata' in param_list and '--convert' in param_list:
    output = unoconverter.getMetadata()
    output['Data'] = unoconverter.convert()
  elif '--setmetadata' in param_list:
    unoconverter.setMetadata(metadata)
    output = document_url

  print output
    
if "__main__" == __name__:
  main()
