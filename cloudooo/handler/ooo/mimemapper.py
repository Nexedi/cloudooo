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

import pkg_resources
from re import findall
from subprocess import Popen, PIPE
from zope.interface import implements
from filter import Filter
from os import environ, path
from cloudooo.interfaces.mimemapper import IMimemapper
from types import InstanceType
import json


class MimeMapper(object):
  """Load all filters from OOo. You can get the filter you want or all
  filters of the specific extension.
  """
  implements(IMimemapper)

  def __init__(self):
    """When it is instantiated, it creates a structure to store filters.
    And lists to store the tags xml.
    """
    self._loaded = False
    self._filter_by_extension_dict = {}
    self._extension_list_by_type = {}
    self._doc_type_list_by_extension = {}
    self._mimetype_by_filter_type = {}
    self._document_type_dict = {}

  def _addFilter(self, filter):
    """Add filter in mimemapper catalog."""
    extension = filter.getExtension()
    if not self._filter_by_extension_dict.has_key(extension):
      self._filter_by_extension_dict[extension] = []
    self._filter_by_extension_dict.get(extension).append(filter)

  def _typeToDocumentService(self, document_type):
    """Returns the document service according to document type."""
    for k, v in self._document_type_dict.iteritems():
      if k.startswith(document_type):
        return v

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

  def isLoaded(self):
    """Verify if filters were loaded"""
    return self._loaded

  def loadFilterList(self, hostname, port, **kw):
    """Load all filters of openoffice.
    Keyword arguments:
      hostname -- host of OpenOffice
      port -- port to connects by socket
    **kw:
      uno_path -- full path to uno library
      office_binary_path -- full path to openoffice binary
    """
    uno_path = kw.get("uno_path", environ.get('uno_path'))
    office_binary_path = kw.get("office_binary_path",
                                environ.get('office_binary_path'))
    python = path.join(office_binary_path, "python")
    command = [path.exists(python) and python or "python",
            pkg_resources.resource_filename(__name__,
                             path.join("helper", "unomimemapper.py")),
            "--uno_path=%s" % uno_path,
            "--office_binary_path=%s" % office_binary_path,
            "--hostname=%s" % hostname,
            "--port=%s" % port]

    stdout, stderr = Popen(command,
                           stdout=PIPE,
                           close_fds=True).communicate()
    filter_dict, type_dict = json.loads(stdout)
    for filter_name, value in filter_dict.iteritems():
      flag = value.get("Flags")
      # http://api.openoffice.org/docs/DevelopersGuide/OfficeDev/OfficeDev.xhtml#1_2_4_2_10_Properties_of_a_Filter
      # Import:0x01, Export:0x02, Template:0x04, Internal:0x08,
      # OwnTemplate:0x10, Own:0x20, Alien:0x40,
      # UsesOptions (deprecated):0x80, Default:0x100,
      # NotInFileDialog:0x1000, NotInChooser:0x2000,
      # ThirdParty:0x80000, Preferred:0x10000000
      if flag & 0x08 or flag & 0x1000 or flag & 0x2000:
        continue
      ui_name = value.get('UIName')
      filter_type = value.get('Type')
      filter_type_dict = type_dict.get(filter_type)
      if not ui_name:
        ui_name = filter_type_dict.get("UIName")
      filter_extension_list = filter_type_dict.get("Extensions")
      mimetype = filter_type_dict.get("MediaType")
      if not (filter_extension_list and mimetype):
        continue
      preferred = filter_type_dict.get("Preferred")
      document_service_str = value.get('DocumentService')
      # these document services are not supported for now.
      if document_service_str in (
        'com.sun.star.text.GlobalDocument',
        'com.sun.star.formula.FormulaProperties',
        'com.sun.star.sdb.OfficeDatabaseDocument'):
        continue
      sort_index = flag

      doc_type = document_service_str.split('.')[-1]
      split_type_list = findall(r'[A-Z][a-z]+', doc_type)
      if len(split_type_list) > 2:
        doc_type = ''.join(split_type_list[:2]).lower()
      else:
        doc_type = split_type_list[0].lower()

      if doc_type not in self._document_type_dict:
        self._document_type_dict[doc_type] = document_service_str

      # for Export filters
      if flag & 0x02:
        if not self._mimetype_by_filter_type.has_key(filter_type):
          self._mimetype_by_filter_type[filter_type] = mimetype
        # for export filters, one extension is enough.
        for ext in filter_extension_list[:1]:
          # Add (extension, ui_name) tuple by document_type.
          # e.g {'com.sun.star.text.TextDocument': [('txt', 'Text'),]}
          self._extension_list_by_type.setdefault(document_service_str, [])
          if not (ext, ui_name) in self._extension_list_by_type[document_service_str]:
            self._extension_list_by_type[document_service_str].append((ext, ui_name))
          # register an export filter
          filter = Filter(ext, filter_name, mimetype, document_service_str,
                          preferred=preferred, sort_index=sort_index, label=ui_name)
          self._addFilter(filter)

      # for Import filters
      if flag & 0x01:
        # for import filters, we care all possible extensions.
        for ext in filter_extension_list:
          # Add a document type by extension.
          # e.g {'doc': ['com.sun.star.text.TextDocument']}
          self._doc_type_list_by_extension.setdefault(ext, [])
          if not document_service_str in self._doc_type_list_by_extension[ext]:
            self._doc_type_list_by_extension[ext].append(document_service_str)

    # hardcode 'extension -> document type' mappings according to
    # soffice behaviour for extensions having several candidates.
    self._doc_type_list_by_extension.update({
      'rtf':['com.sun.star.text.TextDocument'],
      'sxd':['com.sun.star.drawing.DrawingDocument'],
      'txt':['com.sun.star.text.TextDocument'],
      'odg':['com.sun.star.drawing.DrawingDocument'],
      'html':['com.sun.star.text.WebDocument'],
      'sda':['com.sun.star.drawing.DrawingDocument'],
      'sdd':['com.sun.star.drawing.DrawingDocument'],
      'pdf':['com.sun.star.drawing.DrawingDocument'],
      'xls':['com.sun.star.sheet.SpreadsheetDocument'],
      })
    self.document_service_list = self._extension_list_by_type.keys()
    self.extension_list_by_doc_type =\
        dict([(type, [extension[0] for extension in extension_list])\
              for type, extension_list in self._extension_list_by_type.iteritems()])
    self._loaded = True

  def getFilterName(self, extension, document_service):
    """Get filter name according to the parameters passed.
    Keyword arguments:
    extension -- expected a string of the file format.
    document_type -- expected a string of the document type.
    e.g
    >>> mimemapper.getFilterName("sdw", "com.sun.star.text.TextDocument")
    'StarWriter 3.0'
    """
    filter_list = [filter for filter in iter(self.getFilterList(extension)) \
        if filter.getDocumentService() == document_service]
    if len(filter_list) > 1:
      for filter in iter(filter_list):
        if filter.isPreferred():
          return filter.getName()
      else:
        sort_index_list = [filter.getSortIndex() \
            for filter in iter(filter_list)]
        num_max_int = max(sort_index_list)
        for filter in iter(filter_list):
          if filter.getName().endswith("Export"):
            return filter.getName()
        for filter in iter(filter_list):
          if filter.getSortIndex() == num_max_int:
            return filter.getName()
    else:
      return filter_list[0].getName()

  def getFilterList(self, extension):
    """Search filter by extension, and return the filter as string.
    Keyword arguments:
    extension -- expected a string of the file format.
    e.g
    >>> mimemapper.getFilterList("doc")
    [<filter.Filter object at 0x9a2602c>,
    <filter.Filter object at 0x9a21d6c>,
    <filter.Filter object at 0x9a261ec>]
    """
    return self._filter_by_extension_dict.get(extension, [])

  def getAllowedExtensionList(self, extension=None, document_type=None):
    """Returns a list with extensions which can be used to export according to
    document type passed.
    e.g
    >>> mimemapper.getAllowedExtensionList({"extension":"doc"})
    or
    >>> mimemapper.getAllowedExtensionList({"document_type":"text"})
    (('rtf', 'Rich Text Format'),
    ('htm', 'HTML Document'),)
    If both params are passed, document_type is discarded.
    """
    allowed_extension_list = []
    document_type_list = []
    if extension:
      document_type_list.extend(self._doc_type_list_by_extension.get(extension, []))
    elif document_type:
      document_type = self._typeToDocumentService(document_type)
      allowed_extension_list.extend(self._extension_list_by_type.get(document_type, []))
    # gets list of extensions of each document type if document_type_list isn't
    # empty.
    for type in iter(document_type_list):
      # gets list of extensions with key document type
      extension_list = self._extension_list_by_type.get(type)
      for ext in iter(extension_list):
        if not ext in allowed_extension_list:
          allowed_extension_list.append(ext)
    return tuple(allowed_extension_list)

mimemapper = MimeMapper()
