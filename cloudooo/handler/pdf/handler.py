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
import io

from zope.interface import implements
from cloudooo.interfaces.handler import IHandler
from cloudooo.file import File
from cloudooo.util import logger, parseContentType
from subprocess import Popen, PIPE
from tempfile import mktemp

from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import NameObject, createStringObject

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
    # TODO: use pyPdf
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
    # TODO: use pyPdf and not use lower()
    command = ["pdfinfo", self.document.getUrl()]
    stdout, stderr = Popen(command,
                           stdout=PIPE,
                           stderr=PIPE,
                           close_fds=True,
                           env=self.environment).communicate()
    info_list = filter(None, stdout.split("\n"))
    metadata = {}
    for info in iter(info_list):
      info = info.split(":")
      info_name = info[0].lower()
      info_value = ":".join(info[1:]).strip()
      metadata[info_name] = info_value
    self.document.trash()
    return metadata

  def setMetadata(self, metadata):
    """Returns a document with new metadata.
    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    # TODO: date as "D:20090401124817-04'00'" ASN.1 for ModDate and CreationDate
    input_pdf = PdfFileReader(open(self.document.getUrl(), "rb"))
    output_pdf = PdfFileWriter()

    modification_date = metadata.pop("ModificationDate", None)
    if modification_date:
      metadata['ModDate'] = modification_date
    if type(metadata.get('Keywords', None)) is list:
      metadata['Keywords'] = metadata['Keywords'].join(' ')
    args = {}
    for key, value in list(metadata.items()):
      args[NameObject('/' + key.capitalize())] = createStringObject(value)

    output_pdf._info.getObject().update(args)

    for page_num in range(input_pdf.getNumPages()):
      output_pdf.addPage(input_pdf.getPage(page_num))

    output_stream = io.BytesIO()
    output_pdf.write(output_stream)
    return output_stream.getvalue()

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
