##############################################################################
#
# Copyright (c) 2009-2011 Nexedi SA and Contributors. All Rights Reserved.
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
from xml.etree import ElementTree
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile, mktemp
import sys
import os

from zope.interface import implements

from cloudooo.interfaces.handler import IHandler
from cloudooo.file import File
from cloudooo.util import logger, zipTree, unzip

AVS_OFFICESTUDIO_FILE_UNKNOWN = "0"
AVS_OFFICESTUDIO_FILE_DOCUMENT_DOCX = "65"
AVS_OFFICESTUDIO_FILE_PRESENTATION_PPTX = "129"
AVS_OFFICESTUDIO_FILE_PRESENTATION_PPSX = "132"
AVS_OFFICESTUDIO_FILE_SPREADSHEET_XLSX = "257"
AVS_OFFICESTUDIO_FILE_CROSSPLATFORM_PDF = "513"
AVS_OFFICESTUDIO_FILE_TEAMLAB_DOCY = "4097"
AVS_OFFICESTUDIO_FILE_TEAMLAB_XLSY = "4098"
AVS_OFFICESTUDIO_FILE_TEAMLAB_PPTY = "4099"
AVS_OFFICESTUDIO_FILE_CANVAS_WORD = "8193"
AVS_OFFICESTUDIO_FILE_CANVAS_SPREADSHEET = "8194"
AVS_OFFICESTUDIO_FILE_CANVAS_PRESENTATION = "8195"
AVS_OFFICESTUDIO_FILE_OTHER_HTMLZIP = "2051"
AVS_OFFICESTUDIO_FILE_OTHER_ZIP = "2057"

format_code_map = {
  "docy": AVS_OFFICESTUDIO_FILE_CANVAS_WORD,
  "docx": AVS_OFFICESTUDIO_FILE_DOCUMENT_DOCX,
  "xlsy": AVS_OFFICESTUDIO_FILE_CANVAS_SPREADSHEET,
  "xlsx": AVS_OFFICESTUDIO_FILE_SPREADSHEET_XLSX,
  "ppty": AVS_OFFICESTUDIO_FILE_CANVAS_PRESENTATION,
  "pptx": AVS_OFFICESTUDIO_FILE_PRESENTATION_PPTX,
}

yformat_tuple = ("docy", "xlsy", "ppty")

class Handler(object):
  """
  X2T Handler is used to convert Microsoft Office 2007 documents to OnlyOffice
  documents.
  """

  implements(IHandler)

  def __init__(self, base_folder_url, data, source_format, **kw):
    """
    base_folder_url(string)
      The requested url for data base folder
    data(string)
      The opened and readed file into a string
    source_format(string)
      The source format of the inputed file
    """
    self.base_folder_url = base_folder_url
    self.file = File(base_folder_url, data, source_format)
    self.environment = kw.get("env", {})

  def convert(self, destination_format=None, **kw):
    """ Convert the inputed file to output as format that were informed """
    source_format = self.file.source_format
    logger.debug("x2t convert: %s > %s" % (source_format, destination_format))

    # init vars and xml configuration file
    in_format = format_code_map[source_format]
    out_format = format_code_map[destination_format]
    root_dir = self.file.directory_name
    input_dir = os.path.join(root_dir, "input");
    output_dir = os.path.join(root_dir, "output");
    final_file_name = os.path.join(root_dir, "document.%s" % destination_format)
    input_file_name = self.file.getUrl()
    output_file_name = final_file_name
    config_file_name = os.path.join(root_dir, "config.xml")

    if source_format in yformat_tuple:
      os.mkdir(input_dir)
      unzip(self.file.getUrl(), input_dir)
      for _, _, files in os.walk(input_dir):
        input_file_name, = files
        break
      input_file_name = os.path.join(input_dir, input_file_name)
    if destination_format in yformat_tuple:
      os.mkdir(output_dir)
      output_file_name = os.path.join(output_dir, "body.txt")

    config_file = open(config_file_name, "w")

    config = {
      # 'm_sKey': 'from',
      'm_sFileFrom': input_file_name,
      'm_nFormatFrom': in_format,
      'm_sFileTo': output_file_name,
      'm_nFormatTo': out_format,
      # 'm_bPaid': 'true',
      # 'm_bEmbeddedFonts': 'false',
      # 'm_bFromChanges': 'false',
      # 'm_sFontDir': '/usr/share/fonts',
      # 'm_sThemeDir': '/var/www/onlyoffice/documentserver/FileConverterService/presentationthemes',
    }
    root = ElementTree.Element('root')
    for key, value in config.items():
      ElementTree.SubElement(root, key).text = value
    ElementTree.ElementTree(root).write(config_file, encoding='utf-8', xml_declaration=True, default_namespace=None, method="xml")
    config_file.close()

    # run convertion binary
    p = Popen(
      ["x2t", config_file.name],
      stdout=PIPE,
      stderr=PIPE,
      close_fds=True,
      env=self.environment,
    )
    stdout, stderr = p.communicate()
    if p.returncode != 0:
      raise RuntimeError("x2t: exit code %d != 0\n+ %s\n> stdout: %s\n> stderr: %s@ x2t xml:\n%s" % (p.returncode, " ".join(["x2t", config_file.name]), stdout, stderr, "  " + open(config_file.name).read().replace("\n", "\n  ")))

    if destination_format in yformat_tuple:
      zipTree(
        final_file_name,
        (output_file_name, ""),
        (os.path.join(os.path.dirname(output_file_name), "media"), ""),
      )

    self.file.reload(final_file_name)
    try:
      return self.file.getContent()
    finally:
      self.file.trash()

  def getMetadata(self, base_document=False):
    """Returns a dictionary with all metadata of document.
    along with the metadata.
    """
    raise NotImplementedError

  def setMetadata(self, metadata={}):
    """Returns image with new metadata.
    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    raise NotImplementedError
