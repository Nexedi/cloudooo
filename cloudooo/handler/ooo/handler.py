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

import json
import re
import pkg_resources
import mimetypes
from base64 import decodestring, encodestring
from os import environ, path
from subprocess import Popen, PIPE
from cloudooo.handler.ooo.application.openoffice import openoffice
from zope.interface import implements
from cloudooo.interfaces.handler import IHandler
from cloudooo.handler.ooo.mimemapper import mimemapper
from cloudooo.handler.ooo.document import FileSystemDocument
from cloudooo.handler.ooo.monitor.timeout import MonitorTimeout
from cloudooo.handler.ooo.monitor import monitor_sleeping_time
from cloudooo.util import logger, parseContentType
from psutil import pid_exists


class Handler(object):
  """OOO Handler is used to access the one Document and OpenOffice.
  For each Document inputed is created on instance of this class to manipulate
  the document. This Document must be able to create and remove a temporary
  document at FS, load and export.
  """
  implements(IHandler)

  def __init__(self, base_folder_url, data, source_format, **kw):
    """Creates document in file system and loads it in OOo."""
    self.document = FileSystemDocument(base_folder_url,
                                      data,
                                      source_format)
    self.zip = kw.get('zip', False)
    self.uno_path = kw.get("uno_path", None)
    self.office_binary_path = kw.get("office_binary_path", None)
    self.timeout = kw.get("timeout", 600)
    self.refresh = kw.get('refresh', False)
    self.source_format = source_format
    if not self.uno_path:
      self.uno_path = environ.get("uno_path")
    if not self.office_binary_path:
      self.office_binary_path = environ.get("office_binary_path")

  def _getCommand(self, *args, **kw):
    """Transforms all parameters passed in a command"""
    hostname, port = openoffice.getAddress()
    kw['hostname'] = hostname
    kw['port'] = port
    python = path.join(self.office_binary_path, "python")
    command_list = [path.exists(python) and python or "python",
                    pkg_resources.resource_filename(__name__,
                                 path.join("helper", "unoconverter.py")),
                    "--uno_path=%s" % self.uno_path,
                    "--office_binary_path=%s" % self.office_binary_path,
                    '--document_url=%s' % self.document.getUrl()]
    for arg in args:
      command_list.insert(3, "--%s" % arg)
    for k, v in kw.iteritems():
      command_list.append("--%s=%s" % (k, v))

    return command_list

  def _startTimeout(self):
    """start the Monitor"""
    self.monitor = MonitorTimeout(openoffice, self.timeout)
    self.monitor.start()
    return

  def _stopTimeout(self):
    """stop the Monitor"""
    self.monitor.terminate()
    return

  def _subprocess(self, command_list):
    """Run one procedure"""
    if monitor_sleeping_time is not None:
      monitor_sleeping_time.touch()
    try:
      self._startTimeout()
      process = Popen(command_list, stdout=PIPE, stderr=PIPE, close_fds=True,
                      env=openoffice.environment_dict.copy())
      stdout, stderr = process.communicate()
    finally:
      self._stopTimeout()
      if pid_exists(process.pid):
        process.terminate()
    return stdout, stderr

  def _callUnoConverter(self, *feature_list, **kw):
    """ """
    if not openoffice.status():
      openoffice.start()
    command_list = self._getCommand(*feature_list, **kw)
    stdout, stderr = self._subprocess(command_list)
    if not stdout and len(re.findall("\w*Exception|\w*Error", stderr)) >= 1:
      logger.debug(stderr)
      self.document.restoreOriginal()
      openoffice.restart()
      kw['document_url'] = self.document.getUrl()
      command = self._getCommand(*feature_list, **kw)
      stdout, stderr = self._subprocess(command)
      if stderr != "":
          raise Exception(stderr)

    return stdout, stderr

  def _serializeMimemapper(self,
                           source_extension=None,
                           destination_extension=None):
    """Serialize parts of mimemapper"""
    if destination_extension is None:
      return json.dumps(dict(mimetype_by_filter_type=mimemapper._mimetype_by_filter_type))

    filter_list = []
    service_type_list = mimemapper._doc_type_list_by_extension.get(
      source_extension, mimemapper.document_service_list)
    for service_type in service_type_list:
      filter_list.append((destination_extension,
                          service_type,
                          mimemapper.getFilterName(destination_extension, service_type)))
    logger.debug("Filter List: %r" % filter_list)
    return json.dumps(dict(doc_type_list_by_extension=mimemapper._doc_type_list_by_extension,
                            filter_list=filter_list,
                            mimetype_by_filter_type=mimemapper._mimetype_by_filter_type))

  def convert(self, destination_format=None, **kw):
    """Convert a document to another format supported by the OpenOffice
    Keyword Arguments:
    destination_format -- extension of document as String
    """
    logger.debug("OooConvert: %s > %s" % (self.source_format, destination_format))
    kw['source_format'] = self.source_format
    if destination_format:
      kw['destination_format'] = destination_format
    kw['mimemapper'] = self._serializeMimemapper(self.source_format,
                                                 destination_format)
    kw['refresh'] = json.dumps(self.refresh)
    openoffice.acquire()
    try:
      stdout, stderr = self._callUnoConverter(*['convert'], **kw)
    finally:
      openoffice.release()
    url = stdout.replace('\n', '')
    self.document.reload(url)
    content = self.document.getContent(self.zip)
    self.document.trash()
    return content

  def getMetadata(self, base_document=False):
    """Returns a dictionary with all metadata of document.
    Keywords Arguments:
    base_document -- Boolean variable. if true, the document is also returned
    along with the metadata."""
    logger.debug("getMetadata")
    kw = dict(mimemapper=self._serializeMimemapper())
    if base_document:
      feature_list = ['getmetadata', 'convert']
    else:
      feature_list = ['getmetadata']
    openoffice.acquire()
    try:
      stdout, stderr = self._callUnoConverter(*feature_list, **kw)
    finally:
      openoffice.release()
    metadata = json.loads(decodestring(stdout))
    if 'document_url' in metadata:
      self.document.reload(metadata['document_url'])
      metadata['Data'] = self.document.getContent()
      del metadata['document_url']
    self.document.trash()
    return metadata

  def setMetadata(self, metadata):
    """Returns a document with new metadata.
    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    metadata_pickled = json.dumps(metadata)
    logger.debug("setMetadata")
    kw = dict(metadata=encodestring(metadata_pickled))
    openoffice.acquire()
    try:
      stdout, stderr = self._callUnoConverter(*['setmetadata'], **kw)
    finally:
      openoffice.release()
    doc_loaded = self.document.getContent()
    self.document.trash()
    return doc_loaded

  @staticmethod
  def getAllowedConversionFormatList(source_mimetype):
    """Returns a list content_type and their titles which are supported
    by enabled handlers.

    [('application/vnd.oasis.opendocument.text', 'ODF Text Document'),
     ('application/pdf', 'PDF - Portable Document Format'),
     ...
    ]
    """
    # XXX please never guess extension from mimetype
    output_set = set()
    if "/" in source_mimetype:
      parsed_mimetype_type = parseContentType(source_mimetype).gettype()
      # here `guess_all_extensions` never handles mimetype parameters
      #   (even for `text/plain;charset=UTF-8` which is standard)
      extension_list = mimetypes.guess_all_extensions(parsed_mimetype_type)  # XXX never guess
    else:
      extension_list = [source_mimetype]

    for ext in extension_list:
      for ext, title in mimemapper.getAllowedExtensionList(extension=ext.replace(".", "")):
        if ext in ("fodt", ".fodt"):  # BBB
          output_set.add(("application/vnd.oasis.opendocument.text-flat-xml", title))
          continue
        if ext:
          mimetype, _ = mimetypes.guess_type("a." + ext)  # XXX never guess
          if mimetype and mimetype != parsed_mimetype_type:
            output_set.add((mimetype, title))
    return list(output_set)

def bootstrapHandler(configuration_dict):
  # Bootstrap handler
  from signal import signal, SIGINT, SIGQUIT, SIGHUP
  from cloudooo.handler.ooo.mimemapper import mimemapper
  from cloudooo.handler.ooo.application.openoffice import openoffice
  import cloudooo.handler.ooo.monitor as monitor

  def stopProcesses(signum, frame):
    monitor.stop()
    openoffice.stop()

  # Signal to stop all processes
  signal(SIGINT, stopProcesses)
  signal(SIGQUIT, stopProcesses)
  signal(SIGHUP, stopProcesses)

  working_path = configuration_dict.get('working_path')
  application_hostname = configuration_dict.get('application_hostname')
  openoffice_port = int(configuration_dict.get('openoffice_port'))
  environment_dict = configuration_dict['env']
  # Loading Configuration to start OOo Instance and control it
  openoffice.loadSettings(application_hostname,
                          openoffice_port,
                          working_path,
                          configuration_dict.get('office_binary_path'),
                          configuration_dict.get('uno_path'),
                          configuration_dict.get('openoffice_user_interface_language',
                                                 'en'),
                          environment_dict=environment_dict,
                          )
  openoffice.start()
  monitor.load(configuration_dict)

  timeout_response = int(configuration_dict.get('timeout_response'))
  kw = dict(uno_path=configuration_dict.get('uno_path'),
            office_binary_path=configuration_dict.get('office_binary_path'),
            timeout=timeout_response,
            ooo_disable_filter_list=configuration_dict.get('ooo_disable_filter_list'),
            ooo_disable_filter_name_list=configuration_dict.get('ooo_disable_filter_name_list'))

  # Load all filters
  openoffice.acquire()
  mimemapper.loadFilterList(application_hostname,
                            openoffice_port, **kw)
  openoffice.release()
