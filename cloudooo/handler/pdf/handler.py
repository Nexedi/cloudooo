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

from zope.interface import implements
from cloudooo.interfaces.handler import IHandler
from cloudooo.file import File
from cloudooo.util import logger, parseContentType
from subprocess import Popen, PIPE
from tempfile import mktemp


class Handler(object):
  """PDF Handler is used to handler inputed pdf document."""

  implements(IHandler)

  def __init__(self, base_folder_url, data, source_format, **kw):
    """ Load pdf document """
    self.base_folder_url = base_folder_url
    self.document = File(base_folder_url, data, source_format)
    self.environment = kw.get("env", {})

  def convert(self, destination_format=None, **kw):
    """ Convert a pdf document """
    logger.debug("PDFConvert: %s > %s" % (self.document.source_format, destination_format))
    output_url = mktemp(suffix=".%s" % destination_format,
                        dir=self.document.directory_name)
    command = ["pdftotext", self.document.getUrl(), output_url]
    stdout, stderr = Popen(command,
                           stdout=PIPE,
                           stderr=PIPE,
                           close_fds=True,
                           env=self.environment).communicate()
    self.document.reload(output_url)
    try:
      return self.document.getContent()
    finally:
      self.document.trash()

  def getMetadata(self, base_document=False):
    """Returns a dictionary with all metadata of document.
    along with the metadata.
    """
    command = ["pdfinfo", self.document.getUrl()]
    stdout, stderr = Popen(command,
                           stdout=PIPE,
                           stderr=PIPE,
                           close_fds=True,
                           env=self.environment).communicate()
    info_list = filter(None, stdout.split("\n"))
    metadata = {}
    for info in iter(info_list):
      if info.count(":") == 1:
        info_name, info_value = info.split(":")
      else:
        info_name, info_value = info.split("  ")
        info_name = info_name.replace(":", "")
      info_value = info_value.strip()
      metadata[info_name.lower()] = info_value
    self.document.trash()
    return metadata

  def setMetadata(self, metadata):
    """Returns a document with new metadata.
    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    text_template = "InfoKey: %s\nInfoValue: %s\n"
    text_list = [text_template % (key.capitalize(), value) \
                                 for key, value in metadata.iteritems()]
    metadata_file = File(self.document.directory_name,
                         "".join(text_list),
                         "txt")
    output_url = mktemp(suffix=".pdf",
                        dir=self.document.directory_name)
    command = ["pdftk",
               self.document.getUrl(),
               "update_info",
               metadata_file.getUrl(),
               "output",
               output_url
               ]
    stdout, stderr = Popen(command,
                           stdout=PIPE,
                           stderr=PIPE,
                           close_fds=True,
                           env=self.environment).communicate()
    self.document.reload(output_url)
    try:
      return self.document.getContent()
    finally:
      self.document.trash()

  @staticmethod
  def getAllowedConversionFormatList(source_mimetype):
    """Returns a list content_type and their titles which are supported
    by enabled handlers.

    [('text/plain', 'Plain Text'),
     ...
    ]
    """
    source_mimetype = parseContentType(source_mimetype).gettype()
    if source_mimetype in ("application/pdf", "pdf"):
      return [("text/plain", "Plain Text")]
    return []
