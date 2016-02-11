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
from os.path import join, dirname, realpath
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
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

Ext2Formats = {
  "docy": AVS_OFFICESTUDIO_FILE_CANVAS_WORD,
  "docx": AVS_OFFICESTUDIO_FILE_DOCUMENT_DOCX,
  "xlsy": AVS_OFFICESTUDIO_FILE_CANVAS_SPREADSHEET,
  "xlsx": AVS_OFFICESTUDIO_FILE_SPREADSHEET_XLSX,
  "ppty": AVS_OFFICESTUDIO_FILE_CANVAS_PRESENTATION,
  "pptx": AVS_OFFICESTUDIO_FILE_PRESENTATION_PPTX,
}

dir_name = dirname(realpath(sys.argv[0]))
#dir_name = join(dirname(realpath(__file__)), 'bin')
converter_bin = join(dir_name, 'x2t')
converter_lib_dirname = join(dir_name, 'lib')

yformat_map = {
  'docy': 'docx',
  'xlsy': 'xlsx',
  'ppty': 'pptx',
}

yformat_service_map = {
  'docy': 'com.sun.star.text.TextDocument',
  'xlsy': 'com.sun.star.sheet.SpreadsheetDocument',
  'ppty': 'com.sun.star.presentation.PresentationDocument',
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
      The source format of the inputed file"""
    self.base_folder_url = base_folder_url
    self.file = File(base_folder_url, data, source_format)
    self.environment = kw.get("env", {})
    self.environment['LD_LIBRARY_PATH'] = converter_lib_dirname

  def convert(self, destination_format=None, **kw):
    """ Convert the inputed file to output as format that were informed """
    logger.debug("yformat convert x2t: %s > %s" % (self.file.source_format, destination_format))
    in_format = Ext2Formats.get(self.file.source_format)
    out_format = Ext2Formats.get(destination_format)

    with NamedTemporaryFile(suffix='.%s' % destination_format, dir=self.base_folder_url) as output_file:
      config = {
        # 'm_sKey': 'from',
        'm_sFileFrom': self.file.getUrl(),
        'm_nFormatFrom': in_format,
        'm_sFileTo': output_file.name,
        'm_nFormatTo': out_format,
        # 'm_bPaid': 'true',
        # 'm_bEmbeddedFonts': 'false',
        # 'm_bFromChanges': 'false',
        # 'm_sFontDir': '/usr/share/fonts',
        # 'm_sThemeDir': '/var/www/onlyoffice/documentserver/FileConverterService/presentationthemes',
      }
      with NamedTemporaryFile(suffix=".xml", dir=self.base_folder_url) as temp_xml:
        root = ElementTree.Element('root')
        for key, value in config.items():
          ElementTree.SubElement(root, key).text = value
        ElementTree.ElementTree(root).write(temp_xml, encoding='utf-8', xml_declaration=True, default_namespace=None,
                                            method="xml")
        temp_xml.flush()
        p = Popen([converter_bin, temp_xml.name],
                  env=self.environment,
                  stdout=PIPE,
                  stderr=PIPE,
                  close_fds=True,
                  )
        stdout, stderr = p.communicate()
        with open(output_file.name) as output_file1:
          file_content = output_file1.read()
        return_code_msg = "yformat convert x2t return:{}".format(p.returncode)
        if p.returncode != 0 or not file_content:
          raise Exception(return_code_msg + '\n' + stderr)
      logger.debug(stdout)
      logger.debug(stderr)
      logger.debug("yformat convert x2t return:{}".format(p.returncode))
      self.file.trash()
      return file_content

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
