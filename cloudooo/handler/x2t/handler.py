##############################################################################
#
# Copyright (c) 2016-2017 Nexedi SA and Contributors. All Rights Reserved.
#               Boris Kocherov <bk@raskon.ru>
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
import os
import json
import io
from mimetypes import guess_type

from zope.interface import implements

from cloudooo.interfaces.handler import IHandler
from cloudooo.file import File
from cloudooo.util import logger, unzip, parseContentType
from cloudooo.handler.ooo.handler import Handler as OOoHandler

from zipfile import ZipFile, ZIP_DEFLATED

AVS_OFFICESTUDIO_FILE_UNKNOWN = 0x0000

AVS_OFFICESTUDIO_FILE_DOCUMENT = 0x0040
AVS_OFFICESTUDIO_FILE_DOCUMENT_DOCX = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x0001
AVS_OFFICESTUDIO_FILE_DOCUMENT_DOC = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x0002
AVS_OFFICESTUDIO_FILE_DOCUMENT_ODT = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x0003
AVS_OFFICESTUDIO_FILE_DOCUMENT_RTF = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x0004
AVS_OFFICESTUDIO_FILE_DOCUMENT_TXT = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x0005
AVS_OFFICESTUDIO_FILE_DOCUMENT_HTML = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x0006
AVS_OFFICESTUDIO_FILE_DOCUMENT_MHT = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x0007
AVS_OFFICESTUDIO_FILE_DOCUMENT_EPUB = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x0008
AVS_OFFICESTUDIO_FILE_DOCUMENT_FB2 = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x0009
AVS_OFFICESTUDIO_FILE_DOCUMENT_MOBI = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x000a
AVS_OFFICESTUDIO_FILE_DOCUMENT_DOCM = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x000b
AVS_OFFICESTUDIO_FILE_DOCUMENT_DOTX = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x000c
AVS_OFFICESTUDIO_FILE_DOCUMENT_DOTM = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x000d
AVS_OFFICESTUDIO_FILE_DOCUMENT_ODT_FLAT = AVS_OFFICESTUDIO_FILE_DOCUMENT + 0x000e

AVS_OFFICESTUDIO_FILE_PRESENTATION = 0x0080
AVS_OFFICESTUDIO_FILE_PRESENTATION_PPTX = AVS_OFFICESTUDIO_FILE_PRESENTATION + 0x0001
AVS_OFFICESTUDIO_FILE_PRESENTATION_PPT = AVS_OFFICESTUDIO_FILE_PRESENTATION + 0x0002
AVS_OFFICESTUDIO_FILE_PRESENTATION_ODP = AVS_OFFICESTUDIO_FILE_PRESENTATION + 0x0003
AVS_OFFICESTUDIO_FILE_PRESENTATION_PPSX = AVS_OFFICESTUDIO_FILE_PRESENTATION + 0x0004
AVS_OFFICESTUDIO_FILE_PRESENTATION_PPTM = AVS_OFFICESTUDIO_FILE_PRESENTATION + 0x0005
AVS_OFFICESTUDIO_FILE_PRESENTATION_PPSM = AVS_OFFICESTUDIO_FILE_PRESENTATION + 0x0006
AVS_OFFICESTUDIO_FILE_PRESENTATION_POTX = AVS_OFFICESTUDIO_FILE_PRESENTATION + 0x0007
AVS_OFFICESTUDIO_FILE_PRESENTATION_POTM = AVS_OFFICESTUDIO_FILE_PRESENTATION + 0x0008
AVS_OFFICESTUDIO_FILE_PRESENTATION_ODP_FLAT = AVS_OFFICESTUDIO_FILE_PRESENTATION + 0x0009

AVS_OFFICESTUDIO_FILE_SPREADSHEET = 0x0100
AVS_OFFICESTUDIO_FILE_SPREADSHEET_XLSX = AVS_OFFICESTUDIO_FILE_SPREADSHEET + 0x0001
AVS_OFFICESTUDIO_FILE_SPREADSHEET_XLS = AVS_OFFICESTUDIO_FILE_SPREADSHEET + 0x0002
AVS_OFFICESTUDIO_FILE_SPREADSHEET_ODS = AVS_OFFICESTUDIO_FILE_SPREADSHEET + 0x0003
AVS_OFFICESTUDIO_FILE_SPREADSHEET_CSV = AVS_OFFICESTUDIO_FILE_SPREADSHEET + 0x0004
AVS_OFFICESTUDIO_FILE_SPREADSHEET_XLSM = AVS_OFFICESTUDIO_FILE_SPREADSHEET + 0x0005
AVS_OFFICESTUDIO_FILE_SPREADSHEET_XLTX = AVS_OFFICESTUDIO_FILE_SPREADSHEET + 0x0006
AVS_OFFICESTUDIO_FILE_SPREADSHEET_XLTM = AVS_OFFICESTUDIO_FILE_SPREADSHEET + 0x0007
AVS_OFFICESTUDIO_FILE_SPREADSHEET_ODS_FLAT = AVS_OFFICESTUDIO_FILE_SPREADSHEET + 0x0008

AVS_OFFICESTUDIO_FILE_CROSSPLATFORM = 0x0200
AVS_OFFICESTUDIO_FILE_CROSSPLATFORM_PDF = AVS_OFFICESTUDIO_FILE_CROSSPLATFORM + 0x0001
AVS_OFFICESTUDIO_FILE_CROSSPLATFORM_SWF = AVS_OFFICESTUDIO_FILE_CROSSPLATFORM + 0x0002
AVS_OFFICESTUDIO_FILE_CROSSPLATFORM_DJVU = AVS_OFFICESTUDIO_FILE_CROSSPLATFORM + 0x0003
AVS_OFFICESTUDIO_FILE_CROSSPLATFORM_XPS = AVS_OFFICESTUDIO_FILE_CROSSPLATFORM + 0x0004
AVS_OFFICESTUDIO_FILE_CROSSPLATFORM_SVG = AVS_OFFICESTUDIO_FILE_CROSSPLATFORM + 0x0005
AVS_OFFICESTUDIO_FILE_CROSSPLATFORM_HTMLR = AVS_OFFICESTUDIO_FILE_CROSSPLATFORM + 0x0006
AVS_OFFICESTUDIO_FILE_CROSSPLATFORM_HTMLRMenu = AVS_OFFICESTUDIO_FILE_CROSSPLATFORM + 0x0007
AVS_OFFICESTUDIO_FILE_CROSSPLATFORM_HTMLRCanvas = AVS_OFFICESTUDIO_FILE_CROSSPLATFORM + 0x0008

AVS_OFFICESTUDIO_FILE_IMAGE = 0x0400
AVS_OFFICESTUDIO_FILE_IMAGE_JPG = AVS_OFFICESTUDIO_FILE_IMAGE + 0x0001
AVS_OFFICESTUDIO_FILE_IMAGE_TIFF = AVS_OFFICESTUDIO_FILE_IMAGE + 0x0002
AVS_OFFICESTUDIO_FILE_IMAGE_TGA = AVS_OFFICESTUDIO_FILE_IMAGE + 0x0003
AVS_OFFICESTUDIO_FILE_IMAGE_GIF = AVS_OFFICESTUDIO_FILE_IMAGE + 0x0004
AVS_OFFICESTUDIO_FILE_IMAGE_PNG = AVS_OFFICESTUDIO_FILE_IMAGE + 0x0005
AVS_OFFICESTUDIO_FILE_IMAGE_EMF = AVS_OFFICESTUDIO_FILE_IMAGE + 0x0006
AVS_OFFICESTUDIO_FILE_IMAGE_WMF = AVS_OFFICESTUDIO_FILE_IMAGE + 0x0007
AVS_OFFICESTUDIO_FILE_IMAGE_BMP = AVS_OFFICESTUDIO_FILE_IMAGE + 0x0008
AVS_OFFICESTUDIO_FILE_IMAGE_CR2 = AVS_OFFICESTUDIO_FILE_IMAGE + 0x0009
AVS_OFFICESTUDIO_FILE_IMAGE_PCX = AVS_OFFICESTUDIO_FILE_IMAGE + 0x000a
AVS_OFFICESTUDIO_FILE_IMAGE_RAS = AVS_OFFICESTUDIO_FILE_IMAGE + 0x000b
AVS_OFFICESTUDIO_FILE_IMAGE_PSD = AVS_OFFICESTUDIO_FILE_IMAGE + 0x000c
AVS_OFFICESTUDIO_FILE_IMAGE_ICO = AVS_OFFICESTUDIO_FILE_IMAGE + 0x000d

AVS_OFFICESTUDIO_FILE_OTHER = 0x0800
AVS_OFFICESTUDIO_FILE_OTHER_EXTRACT_IMAGE = AVS_OFFICESTUDIO_FILE_OTHER + 0x0001
AVS_OFFICESTUDIO_FILE_OTHER_MS_OFFCRYPTO = AVS_OFFICESTUDIO_FILE_OTHER + 0x0002
AVS_OFFICESTUDIO_FILE_OTHER_HTMLZIP = AVS_OFFICESTUDIO_FILE_OTHER + 0x0003
AVS_OFFICESTUDIO_FILE_OTHER_OLD_DOCUMENT = AVS_OFFICESTUDIO_FILE_OTHER + 0x0004
AVS_OFFICESTUDIO_FILE_OTHER_OLD_PRESENTATION = AVS_OFFICESTUDIO_FILE_OTHER + 0x0005
AVS_OFFICESTUDIO_FILE_OTHER_OLD_DRAWING = AVS_OFFICESTUDIO_FILE_OTHER + 0x0006
AVS_OFFICESTUDIO_FILE_OTHER_TEAMLAB_INNER = AVS_OFFICESTUDIO_FILE_OTHER + 0x0007
AVS_OFFICESTUDIO_FILE_OTHER_JSON = AVS_OFFICESTUDIO_FILE_OTHER + 0x0008
AVS_OFFICESTUDIO_FILE_OTHER_ZIP = AVS_OFFICESTUDIO_FILE_OTHER + 0x0009

AVS_OFFICESTUDIO_FILE_TEAMLAB = 0x1000
AVS_OFFICESTUDIO_FILE_TEAMLAB_DOCY = AVS_OFFICESTUDIO_FILE_TEAMLAB + 0x0001
AVS_OFFICESTUDIO_FILE_TEAMLAB_XLSY = AVS_OFFICESTUDIO_FILE_TEAMLAB + 0x0002
AVS_OFFICESTUDIO_FILE_TEAMLAB_PPTY = AVS_OFFICESTUDIO_FILE_TEAMLAB + 0x0003

AVS_OFFICESTUDIO_FILE_CANVAS = 0x2000
AVS_OFFICESTUDIO_FILE_CANVAS_WORD = AVS_OFFICESTUDIO_FILE_CANVAS + 0x0001
AVS_OFFICESTUDIO_FILE_CANVAS_SPREADSHEET = AVS_OFFICESTUDIO_FILE_CANVAS + 0x0002
AVS_OFFICESTUDIO_FILE_CANVAS_PRESENTATION = AVS_OFFICESTUDIO_FILE_CANVAS + 0x0003
AVS_OFFICESTUDIO_FILE_CANVAS_PDF = AVS_OFFICESTUDIO_FILE_CANVAS + 0x0004

format_code_map = {
  "odt":  AVS_OFFICESTUDIO_FILE_DOCUMENT_ODT,
  "ods":  AVS_OFFICESTUDIO_FILE_SPREADSHEET_ODS,
  "odp":  AVS_OFFICESTUDIO_FILE_PRESENTATION_ODP,
  "docx": AVS_OFFICESTUDIO_FILE_DOCUMENT_DOCX,
  "xlsx": AVS_OFFICESTUDIO_FILE_SPREADSHEET_XLSX,
  "pptx": AVS_OFFICESTUDIO_FILE_PRESENTATION_PPTX,
  "docy": AVS_OFFICESTUDIO_FILE_CANVAS_WORD,
  "xlsy": AVS_OFFICESTUDIO_FILE_CANVAS_SPREADSHEET,
  "ppty": AVS_OFFICESTUDIO_FILE_CANVAS_PRESENTATION,
}

format_code_map_output = {
  "docy": AVS_OFFICESTUDIO_FILE_TEAMLAB_DOCY,
  "xlsy": AVS_OFFICESTUDIO_FILE_TEAMLAB_XLSY,
  "ppty": AVS_OFFICESTUDIO_FILE_TEAMLAB_PPTY,
}

yformat_map = {
  'docy': 'docx',
  'xlsy': 'xlsx',
  'ppty': 'pptx',
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
    self._data = data
    self._source_format = source_format
    self._init_kw = kw
    self.file = File(base_folder_url, data, source_format)
    self.environment = kw.get("env", {})

  def convert(self, destination_format=None, **kw):
    """ Convert the inputed file to output as format that were informed """
    source_format = self.file.source_format
    logger.debug("x2t convert: %s > %s" % (source_format, destination_format))

    # init vars and xml configuration file
    in_format = format_code_map[source_format]
    out_format = format_code_map_output.get(destination_format,
                                            format_code_map[destination_format])
    root_dir = self.file.directory_name
    input_dir = os.path.join(root_dir, "input");
    input_file_name = self.file.getUrl()
    output_file_name = os.path.join(root_dir, "document.%s" % destination_format)
    config_file_name = os.path.join(root_dir, "config.xml")
    metadata = None
    output_data = None

    if source_format in yformat_tuple:
      if self._data.startswith("PK\x03\x04"):
        os.mkdir(input_dir)
        unzip(self.file.getUrl(), input_dir)
        input_file_name = os.path.join(input_dir, "body.txt")
        if not os.path.isfile(input_file_name):
          input_file_name = os.path.join(input_dir, "Editor.bin")
          if not os.path.isfile(input_file_name):
            raise RuntimeError("input format incorrect: Editor.bin absent in zip archive")
        metadata_file_name = os.path.join(input_dir, "metadata.json")
        if os.path.isfile(metadata_file_name):
          with open(metadata_file_name) as metadata_file:
            metadata = json.loads(metadata_file.read())

    with open(config_file_name, "w") as config_file:
      config = {
        # 'm_sKey': 'from',
        'm_sFileFrom': input_file_name,
        'm_nFormatFrom': str(in_format),
        'm_sFileTo': output_file_name,
        'm_nFormatTo': str(out_format),
        # 'm_bPaid': 'true',
        # 'm_bEmbeddedFonts': 'false',
        # 'm_bFromChanges': 'false',
        # 'm_sFontDir': '/usr/share/fonts',
        # 'm_sThemeDir': '/var/www/onlyoffice/documentserver/FileConverterService/presentationthemes',
      }
      root = ElementTree.Element('root')
      for key, value in config.items():
        ElementTree.SubElement(root, key).text = value
      ElementTree.ElementTree(root).write(config_file, encoding='utf-8', xml_declaration=True,
                                          default_namespace=None, method="xml")

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
      raise RuntimeError("x2t: exit code %d != 0\n+ %s\n> stdout: %s\n> stderr: %s@ x2t xml:\n%s"
                         % (p.returncode, " ".join(["x2t", config_file.name]), stdout, stderr,
                            "  " + open(config_file.name).read().replace("\n", "\n  ")))

    self.file.reload(output_file_name)
    try:
      if source_format in yformat_tuple:
        if metadata:
          output_data = OOoHandler(self.base_folder_url, self.file.getContent(), source_format, **self._init_kw)\
            .setMetadata(metadata)
        else:
          output_data = self.file.getContent()
      elif destination_format in yformat_tuple:
        if not metadata:
          if source_format not in yformat_tuple:
            metadata = OOoHandler(self.base_folder_url, self._data, source_format, **self._init_kw).getMetadata()
          if not metadata:
            metadata = {}
          metadata.pop('MIMEType', None)
          metadata.pop('Generator', None)
          metadata.pop('AppVersion', None)
          metadata.pop('ImplementationName', None)
        with ZipFile(output_file_name, mode="a") as zipfile:
          zipfile.writestr("metadata.json", json.dumps(metadata))
        output_data = self.file.getContent()
    finally:
      self.file.trash()
    return output_data

  def _getContentType(self):
    mimetype_type = None
    if "/" not in self._source_format:
      mimetype_type = guess_type('a.' + self._source_format)[0]
    if mimetype_type is None:
      mimetype_type = self._source_format
    return mimetype_type

  def getMetadata(self, base_document=False):
    r"""Returns a dictionary with all metadata of document.
    """
    if self._source_format in yformat_tuple and self._data.startswith("PK\x03\x04"):
      if base_document:
        openxml_format = yformat_map[self._source_format]
        data = self.convert(yformat_map[self._source_format])
        return OOoHandler(self.base_folder_url, data, openxml_format, **self._init_kw).getMetadata(base_document)
      else:
        with io.BytesIO(self._data) as memfile, ZipFile(memfile) as zipfile:
          try:
            metadata = zipfile.read("metadata.json")
          except KeyError:
            metadata = '{}'
          metadata = json.loads(metadata)
          metadata['MIMEType'] = self._getContentType()
          return metadata
    else:
      return OOoHandler(self.base_folder_url, self._data, self._source_format, **self._init_kw)\
        .getMetadata(base_document)

  def setMetadata(self, metadata=None):
    r"""Returns document with new metadata.
    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    if metadata is None:
      metadata = {}
    if self._source_format in yformat_tuple and self._data.startswith("PK\x03\x04"):
      root_dir = self.file.directory_name
      output_file_name = os.path.join(root_dir, "tmp")
      try:
        input_dir = os.path.join(root_dir, "input")
        os.mkdir(input_dir)
        unzip(self.file.getUrl(), input_dir)
        with open(os.path.join(input_dir, "metadata.json"), "w") as metadata_file:
          metadata_file.write(json.dumps(metadata))
        with ZipFile(output_file_name, "w") as zipfile:
          for root, _, files in os.walk(input_dir):
            relative_root = root.replace(input_dir, '')
            for file_name in files:
              absolute_path = os.path.join(root, file_name)
              file_name = os.path.join(relative_root, file_name)
              zipfile.write(absolute_path, file_name)
        output_data = open(output_file_name).read()
      finally:
        os.unlink(output_file_name)
      return output_data
    else:
      return OOoHandler(self.base_folder_url, self._data, self._source_format, **self._init_kw).setMetadata(metadata)

  @staticmethod
  def getAllowedConversionFormatList(source_mimetype):
    """Returns a list content_type and their titles which are supported
    by enabled handlers.

    [('application/x-asc-text', 'OnlyOffice Text Document'),
     ...
    ]
    """
    source_mimetype = parseContentType(source_mimetype).gettype()
    if source_mimetype in ("docy", "application/x-asc-text"):
      return [
        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "Word 2007 Document"),
        ("application/vnd.oasis.opendocument.text", "ODF Text Document"),
      ]
    if source_mimetype in ("xlsy", "application/x-asc-spreadsheet"):
      return [
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Excel 2007 Spreadsheet"),
        ("application/vnd.oasis.opendocument.spreadsheet", "ODF Spreadsheet Document"),
      ]
    if source_mimetype in ("ppty", "application/x-asc-presentation"):
      return [
        ("application/vnd.openxmlformats-officedocument.presentationml.presentation", "PowerPoint 2007 Presentation"),
        ("application/vnd.oasis.opendocument.presentation", "ODF Presentation Document"),
      ]

    get_format_list = OOoHandler.getAllowedConversionFormatList
    format_list = get_format_list(source_mimetype)
    format_list_append = format_list.append
    for f_type, _ in format_list:
      if f_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        format_list_append(("application/x-asc-text", "OnlyOffice Text Document"))
        break
      if f_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        format_list_append(("application/x-asc-spreadsheet", "OnlyOffice Spreadsheet"))
        break
      if f_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        format_list_append(("application/x-asc-presentation", "OnlyOffice Presentation"))
        break
    return format_list
