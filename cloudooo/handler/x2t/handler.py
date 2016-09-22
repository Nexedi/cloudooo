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

from zope.interface import implements

from cloudooo.interfaces.handler import IHandler
from cloudooo.file import File
from cloudooo.util import logger

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


class Handler(object):
  """ImageMagic Handler is used to handler images."""

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
    #self.environment['LD_LIBRARY_PATH'] = converter_lib_dirname

  def convert(self, destination_format=None, **kw):
    """ Convert the inputed file to output as format that were informed """
    logger.debug("x2t convert: %s > %s" % (self.file.source_format, destination_format))

    in_format = format_code_map[self.file.source_format]
    out_format = format_code_map[destination_format]

    # create files in folder which will be trashed
    output_file_name = mktemp(suffix=".%s" % destination_format, dir=self.file.directory_name)
    temp_xml = NamedTemporaryFile(suffix=".xml", dir=self.file.directory_name, delete=False)

    # write xml configuration file
    config = {
      # 'm_sKey': 'from',
      'm_sFileFrom': self.file.getUrl(),
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
    ElementTree.ElementTree(root).write(temp_xml, encoding='utf-8', xml_declaration=True, default_namespace=None, method="xml")
    temp_xml.close()

    # run convertion binary
    p = Popen(
      ["x2t", temp_xml.name],
      stdout=PIPE,
      stderr=PIPE,
      close_fds=True,
      env=self.environment,
    )
    stdout, stderr = p.communicate()
    if p.returncode != 0:
      raise RuntimeError("x2t: exit code %d != 0\n+ %s\n> stdout: %s\n> stderr: %s@ x2t xml:\n%s" % (p.returncode, " ".join(["x2t", temp_xml.name]), stdout, stderr, "  " + open(temp_xml.name).read().replace("\n", "\n  ")))

    self.file.reload(output_file_name)
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
