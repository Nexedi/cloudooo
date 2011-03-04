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

from zope.interface import implements
from cloudooo.interfaces.handler import IHandler
from cloudooo.file import File
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
    output_url = mktemp(suffix=".%s" % destination_format,
                        dir=self.document.directory_name)
    command = ["pdftotext", self.document.getUrl(), output_url]
    stdout, stderr = Popen(command,
                           stdout=PIPE,
                           stderr=PIPE,
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
                           env=self.environment).communicate()
    self.document.reload(output_url)
    try:
      return self.document.getContent()
    finally:
      self.document.trash()
