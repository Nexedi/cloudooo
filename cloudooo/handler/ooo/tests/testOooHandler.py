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

import magic
from os import path
from base64 import encodestring, decodestring
from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite
from cloudooo.handler.ooo.handler import Handler
from cloudooo.handler.ooo.application.openoffice import openoffice
import os
from lxml import etree
from zipfile import ZipFile

OPENOFFICE = True


class TestHandler(HandlerTestCase):
  """Test OOO Handler and manipulation of OOo Instance"""

  _file_path_list = []

  def _save_document(self, document_output_url, data):
    """Create document in file system"""
    new_file = open(document_output_url, "w")
    new_file.write(data)
    new_file.close()
    self._file_path_list.append(document_output_url)

  def _assert_document_output(self, document, expected_mimetype):
    """Check if the document was created correctly"""
    mime = magic.Magic(mime=True)
    mimetype = mime.from_buffer(document)
    self.assertEquals(mimetype, expected_mimetype)

  def tearDown(self):
    """Cleanup temp files
    """
    while self._file_path_list:
      file_path = self._file_path_list.pop()
      if os.path.exists(file_path):
        os.remove(file_path)
    HandlerTestCase.tearDown(self)

  def testConvertOdtToDoc(self):
    """Test convert ODT to DOC"""
    data = encodestring(open("data/test.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt')
    doc_exported = handler.convert("doc")
    self._assert_document_output(doc_exported, "application/msword")

  def testConvertDocToOdt(self):
    """Test convert DOC to ODT"""
    data = encodestring(open("data/test.doc").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'doc')
    doc_exported = handler.convert("odt")
    self._assert_document_output(doc_exported,
                          "application/vnd.oasis.opendocument.text")

  def testGetMetadata(self):
    """Test getMetadata"""
    data = encodestring(open("data/test.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt')
    metadata = handler.getMetadata()
    self.assertEquals(metadata.get('MIMEType'),
                      'application/vnd.oasis.opendocument.text')
    handler.document.restoreOriginal()
    metadata = handler.getMetadata(True)
    self.assertNotEquals(metadata.get('Data'), '')

  def testSetMetadata(self):
    """Test setMetadata"""
    data = encodestring(open("data/test.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt')
    new_data = handler.setMetadata({"Title": "cloudooo Test -"})
    new_handler = Handler(self.tmp_url,
                            new_data,
                            'odt')
    metadata = new_handler.getMetadata()
    self.assertEquals(metadata.get('Title'), "cloudooo Test -")
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt')
    new_data = handler.setMetadata({"Title": "Namie's working record"})
    new_handler = Handler(self.tmp_url,
                            new_data,
                            'odt')
    metadata = new_handler.getMetadata()
    self.assertEquals(metadata.get('Title'), "Namie's working record")

  def testConvertWithOpenOfficeStopped(self):
    """Test convert with openoffice stopped"""
    openoffice.stop()
    data = encodestring(open("data/test.doc").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'doc')
    doc_exported = handler.convert("odt")
    self._assert_document_output(doc_exported,
                          "application/vnd.oasis.opendocument.text")

  def testGetMetadataWithOpenOfficeStopped(self):
    """Test getMetadata with openoffice stopped"""
    openoffice.stop()
    data = encodestring(open("data/test.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt')
    metadata = handler.getMetadata()
    self.assertEquals(metadata.get('Title'), 'title')
    self.assertEquals(metadata.get('MIMEType'),
              'application/vnd.oasis.opendocument.text')

  def testSetMetadataWithOpenOfficeStopped(self):
    """Test setMetadata with openoffice stopped"""
    openoffice.stop()
    data = encodestring(open("data/test.doc").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'doc')
    new_data = handler.setMetadata({"Title": "cloudooo Test -"})
    new_handler = Handler(self.tmp_url,
                            new_data,
                            'doc')
    metadata = new_handler.getMetadata()
    self.assertEquals(metadata.get('Title'), "cloudooo Test -")

  def testRefreshOdt(self):
    """Test refresh argument"""
    # Check when refreshing is disabled
    data = encodestring(open("data/test_fields.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt',
                        refresh=False)
    doc_exported = handler.convert("odt")
    document_output_url = path.join(self.tmp_url, "testExport.odt")
    self._save_document(document_output_url, doc_exported)
    zip_handler = ZipFile(document_output_url)
    content_tree = etree.fromstring(zip_handler.read('content.xml'))
    self.assertFalse(content_tree.xpath('//text:variable-get[text() = "DISPLAY ME"]',
                                       namespaces=content_tree.nsmap))

    # Check when refreshing is enabled
    data = encodestring(open("data/test_fields.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt',
                        refresh=True)
    doc_exported = handler.convert("odt")
    document_output_url = path.join(self.tmp_url, "testExport.odt")
    self._save_document(document_output_url, doc_exported)
    zip_handler = ZipFile(document_output_url)
    content_tree = etree.fromstring(zip_handler.read('content.xml'))
    self.assertTrue(content_tree.xpath('//text:variable-get[text() = "DISPLAY ME"]',
                                       namespaces=content_tree.nsmap))

  def testGetAllowedConversionFormatList_TextPlain(self):
    """Test allowed conversion format for text/plain with charset parameter"""
    def get(*args, **kw):
      return sorted(Handler.getAllowedConversionFormatList(*args, **kw))
    text_plain_output_list = [
      ('application/msword', 'Microsoft Word 97-2003'),
      ('application/pdf', 'PDF - Portable Document Format'),
      ('application/rtf', 'Rich Text'),
      ('application/vnd.oasis.opendocument.text', 'ODF Text Document'),
      ('application/vnd.oasis.opendocument.text-flat-xml', 'Flat XML ODF Text Document'),
      ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Microsoft Word 2007-2013 XML'),
      ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Office Open XML Text'),
      ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
      ('image/png', 'PNG - Portable Network Graphic'),
      ('text/html', 'HTML Document (Writer)')]
    self.assertEquals(get("text/plain;ignored=param"), text_plain_output_list)
    self.assertEquals(get("text/plain;charset=UTF-8;ignored=param"), text_plain_output_list)
    self.assertEquals(get("text/plain;charset=US-ASCII;ignored=param"), text_plain_output_list)

  def testGetAllowedConversionFormatList_ApplicationMsword(self):
    """Test allowed conversion format for application/msword"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/msword;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/rtf', 'Rich Text'),
        ('application/vnd.oasis.opendocument.text', 'ODF Text Document'),
        ('application/vnd.oasis.opendocument.text-flat-xml', 'Flat XML ODF Text Document'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Microsoft Word 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Office Open XML Text'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('text/html', 'HTML Document (Writer)'),
        ('text/plain', 'Text - Choose Encoding') ])

  def testGetAllowedConversionFormatList_ApplicationPdf(self):
    """Test allowed conversion format for application/pdf"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/pdf;ignored=param")),
      [ ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_TextRtf(self):
    """Test allowed conversion format for text/rtf"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("text/rtf;ignored=param")),
      [])

  def testGetAllowedConversionFormatList_ApplicationVndOasisOpendocumentText(self):
    """Test allowed conversion format for application/vnd.oasis.opendocument.text"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.oasis.opendocument.text;ignored=param")),
      [ ('application/msword', 'Microsoft Word 97-2003'),
        ('application/pdf', 'PDF - Portable Document Format'),
        ('application/rtf', 'Rich Text'),
        ('application/vnd.oasis.opendocument.text-flat-xml', 'Flat XML ODF Text Document'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Microsoft Word 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Office Open XML Text'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('text/html', 'HTML Document (Writer)'),
        ('text/plain', 'Text - Choose Encoding') ])

  def testGetAllowedConversionFormatList_ApplicationVndOasisOpendocumentTextFlatXml(self):
    """Test allowed conversion format for application/vnd.oasis.opendocument.text-flat-xml"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.oasis.opendocument.text-flat-xml;ignored=param")),
      [])

  def testGetAllowedConversionFormatList_ApplicationVndOpenxmlformatsOfficedocumentWordprocessingmlDocument(self):
    """Test allowed conversion format for application/vnd.openxmlformats-officedocument.wordprocessingml.document"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.openxmlformats-officedocument.wordprocessingml.document;ignored=param")),
      [ ('application/msword', 'Microsoft Word 97-2003'),
        ('application/pdf', 'PDF - Portable Document Format'),
        ('application/rtf', 'Rich Text'),
        ('application/vnd.oasis.opendocument.text', 'ODF Text Document'),
        ('application/vnd.oasis.opendocument.text-flat-xml', 'Flat XML ODF Text Document'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('text/html', 'HTML Document (Writer)'),
        ('text/plain', 'Text - Choose Encoding') ])

  def testGetAllowedConversionFormatList_ImageJpeg(self):
    """Test allowed conversion format for image/jpeg"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/jpeg;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ImagePng(self):
    """Test allowed conversion format for image/png"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/png;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_TextHtml(self):
    """Test allowed conversion format for text/html"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("text/html;ignored=param")),
      [ ('application/msword', 'Microsoft Word 97-2003'),
        ('application/pdf', 'PDF - Portable Document Format'),
        ('application/rtf', 'Rich Text'),
        ('application/vnd.ms-excel', 'Microsoft Excel 97-2003'),
        ('application/vnd.ms-excel.sheet.macroEnabled.12', 'Microsoft Excel 2007-2016 XML (macro enabled)'),
        ('application/vnd.oasis.opendocument.spreadsheet', 'ODF Spreadsheet'),
        ('application/vnd.oasis.opendocument.text', 'ODF Text Document'),
        ('application/vnd.oasis.opendocument.text', 'Text (Writer/Web)'),
        ('application/vnd.oasis.opendocument.text-flat-xml', 'Flat XML ODF Text Document'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Microsoft Excel 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Office Open XML Spreadsheet'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Microsoft Word 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Office Open XML Text'),
        ('application/vnd.sun.xml.writer', 'OpenOffice.org 1.0 Text Document (Writer/Web)'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('text/csv', 'Text CSV'),
        ('text/plain', 'Text (Writer/Web)'),
        ('text/plain', 'Text - Choose Encoding'),
        ('text/plain', 'Text - Choose Encoding (Writer/Web)') ])

  def testGetAllowedConversionFormatList_ApplicationPostscript(self):
    """Test allowed conversion format for application/postscript"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/postscript;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ApplicationVndOasisOpendocumentGraphics(self):
    """Test allowed conversion format for application/vnd.oasis.opendocument.graphics"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.oasis.opendocument.graphics;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ImageGif(self):
    """Test allowed conversion format for image/gif"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/gif;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ImageSvgXml(self):
    """Test allowed conversion format for image/svg+xml"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/svg+xml;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ImageTiff(self):
    """Test allowed conversion format for image/tiff"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/tiff;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ImageXCmuRaster(self):
    """Test allowed conversion format for image/x-cmu-raster"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/x-cmu-raster;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ImageBmp(self):
    """Test allowed conversion format for image/x-ms-bmp"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/x-ms-bmp;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ImageXPortableBitmap(self):
    """Test allowed conversion format for image/x-portable-bitmap"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/x-portable-bitmap;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ImageXPortableGraymap(self):
    """Test allowed conversion format for image/x-portable-graymap"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/x-portable-graymap;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ImageXPortablePixmap(self):
    """Test allowed conversion format for image/x-portable-pixmap"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/x-portable-pixmap;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ImageXXpixmap(self):
    """Test allowed conversion format for image/x-xpixmap"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("image/x-xpixmap;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('text/html', 'HTML Document (Draw)') ])

  def testGetAllowedConversionFormatList_ApplicationVndMsExcel(self):
    """Test allowed conversion format for application/vnd.ms-excel"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.ms-excel;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/vnd.ms-excel.sheet.macroEnabled.12', 'Microsoft Excel 2007-2016 XML (macro enabled)'),
        ('application/vnd.oasis.opendocument.spreadsheet', 'ODF Spreadsheet'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Microsoft Excel 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Office Open XML Spreadsheet'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('text/csv', 'Text CSV'),
        ('text/html', 'HTML Document (Calc)') ])

  def testGetAllowedConversionFormatList_ApplicationVndMsExcelSheetMacroenabled12(self):
    """Test allowed conversion format for application/vnd.ms-excel.sheet.macroEnabled.12"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.ms-excel.sheet.macroEnabled.12;ignored=param")),
      [])

  def testGetAllowedConversionFormatList_ApplicationVndOasisOpendocumentSpreadsheet(self):
    """Test allowed conversion format for application/vnd.oasis.opendocument.spreadsheet"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.oasis.opendocument.spreadsheet;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/vnd.ms-excel', 'Microsoft Excel 97-2003'),
        ('application/vnd.ms-excel.sheet.macroEnabled.12', 'Microsoft Excel 2007-2016 XML (macro enabled)'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Microsoft Excel 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Office Open XML Spreadsheet'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('text/csv', 'Text CSV'),
        ('text/html', 'HTML Document (Calc)') ])

  def testGetAllowedConversionFormatList_ApplicationVndOpenXmlFormatsOfficedocumentSpreadsheetmlSheet(self):
    """Test allowed conversion format for application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/vnd.ms-excel', 'Microsoft Excel 97-2003'),
        ('application/vnd.ms-excel.sheet.macroEnabled.12', 'Microsoft Excel 2007-2016 XML (macro enabled)'),
        ('application/vnd.oasis.opendocument.spreadsheet', 'ODF Spreadsheet'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('text/csv', 'Text CSV'),
        ('text/html', 'HTML Document (Calc)') ])

  def testGetAllowedConversionFormatList_ApplicationVndSunXmlWriter(self):
    """Test allowed conversion format for application/vnd.sun.xml.writer"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.sun.xml.writer;ignored=param")),
      [ ('application/msword', 'Microsoft Word 97-2003'),
        ('application/pdf', 'PDF - Portable Document Format'),
        ('application/rtf', 'Rich Text'),
        ('application/vnd.oasis.opendocument.text', 'ODF Text Document'),
        ('application/vnd.oasis.opendocument.text-flat-xml', 'Flat XML ODF Text Document'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Microsoft Word 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Office Open XML Text'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('text/html', 'HTML Document (Writer)'),
        ('text/plain', 'Text - Choose Encoding') ])

  def testGetAllowedConversionFormatList_TextCsv(self):
    """Test allowed conversion format for text/csv"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("text/csv;ignored=param")),
      [ ('application/msword', 'Microsoft Word 97-2003'),
        ('application/pdf', 'PDF - Portable Document Format'),
        ('application/rtf', 'Rich Text'),
        ('application/vnd.ms-excel', 'Microsoft Excel 97-2003'),
        ('application/vnd.ms-excel.sheet.macroEnabled.12', 'Microsoft Excel 2007-2016 XML (macro enabled)'),
        ('application/vnd.oasis.opendocument.spreadsheet', 'ODF Spreadsheet'),
        ('application/vnd.oasis.opendocument.text', 'ODF Text Document'),
        ('application/vnd.oasis.opendocument.text', 'Text (Writer/Web)'),
        ('application/vnd.oasis.opendocument.text-flat-xml', 'Flat XML ODF Text Document'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Microsoft Excel 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Office Open XML Spreadsheet'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Microsoft Word 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Office Open XML Text'),
        ('application/vnd.sun.xml.writer', 'OpenOffice.org 1.0 Text Document (Writer/Web)'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('text/html', 'HTML Document'),
        ('text/html', 'HTML Document (Calc)'),
        ('text/html', 'HTML Document (Writer)'),
        ('text/plain', 'Text (Writer/Web)'),
        ('text/plain', 'Text - Choose Encoding'),
        ('text/plain', 'Text - Choose Encoding (Writer/Web)') ])

  def testGetAllowedConversionFormatList_ApplicationVndOasisOpendocumentPresentation(self):
    """Test allowed conversion format for application/vnd.oasis.opendocument.presentation"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.oasis.opendocument.presentation;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.ms-powerpoint', 'Microsoft PowerPoint 97-2003'),
        ('application/vnd.ms-powerpoint', 'Microsoft PowerPoint 97-2003 AutoPlay'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing (Impress)'),
        ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'Microsoft PowerPoint 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'Office Open XML Presentation'),
        ('application/vnd.openxmlformats-officedocument.presentationml.slideshow', 'Microsoft PowerPoint 2007-2013 XML AutoPlay'),  # TEST it
        ('application/vnd.openxmlformats-officedocument.presentationml.slideshow', 'Office Open XML Presentation AutoPlay'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Impress)') ])

  def testGetAllowedConversionFormatList_ApplicationVndOpenxmlformatsOfficedocumentPresentationmlPresentation(self):
    """Test allowed conversion format for application/vnd.openxmlformats-officedocument.presentationml.presentation"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.openxmlformats-officedocument.presentationml.presentation;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.ms-powerpoint', 'Microsoft PowerPoint 97-2003'),
        ('application/vnd.ms-powerpoint', 'Microsoft PowerPoint 97-2003 AutoPlay'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing (Impress)'),
        ('application/vnd.oasis.opendocument.presentation', 'ODF Presentation'),
        ('application/vnd.openxmlformats-officedocument.presentationml.slideshow', 'Microsoft PowerPoint 2007-2013 XML AutoPlay'),
        ('application/vnd.openxmlformats-officedocument.presentationml.slideshow', 'Office Open XML Presentation AutoPlay'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Impress)') ])

  def testGetAllowedConversionFormatList_ApplicationVndOpenxmlformatsOfficedocumentPresentationmlSlideshow(self):
    """Test allowed conversion format for application/vnd.openxmlformats-officedocument.presentationml.slideshow"""
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.openxmlformats-officedocument.presentationml.slideshow;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.ms-powerpoint', 'Microsoft PowerPoint 97-2003'),
        ('application/vnd.ms-powerpoint', 'Microsoft PowerPoint 97-2003 AutoPlay'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing (Impress)'),
        ('application/vnd.oasis.opendocument.presentation', 'ODF Presentation'),
        ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'Microsoft PowerPoint 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'Office Open XML Presentation'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Impress)') ])

  def testGetAllowedConversionFormatList_ApplicationVndMsPowerpoint(self):
    """Test allowed conversion format for application/vnd.ms-powerpoint"""
    self.maxDiff = None
    self.assertEquals(
      sorted(Handler.getAllowedConversionFormatList("application/vnd.ms-powerpoint;ignored=param")),
      [ ('application/pdf', 'PDF - Portable Document Format'),
        ('application/postscript', 'EPS - Encapsulated PostScript'),
        ('application/vnd.oasis.opendocument.graphics', 'ODF Drawing (Impress)'),
        ('application/vnd.oasis.opendocument.presentation', 'ODF Presentation'),
        ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'Microsoft PowerPoint 2007-2013 XML'),
        ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'Office Open XML Presentation'),
        ('application/vnd.openxmlformats-officedocument.presentationml.slideshow', 'Microsoft PowerPoint 2007-2013 XML AutoPlay'),
        ('application/vnd.openxmlformats-officedocument.presentationml.slideshow', 'Office Open XML Presentation AutoPlay'),
        ('image/gif', 'GIF - Graphics Interchange Format'),
        ('image/jpeg', 'JPEG - Joint Photographic Experts Group'),
        ('image/png', 'PNG - Portable Network Graphic'),
        ('image/svg+xml', 'SVG - Scalable Vector Graphics'),
        ('image/tiff', 'TIFF - Tagged Image File Format'),
        ('image/x-cmu-raster', 'RAS - Sun Raster Image'),
        ('image/x-ms-bmp', 'BMP - Windows Bitmap'),
        ('image/x-portable-bitmap', 'PBM - Portable Bitmap'),
        ('image/x-portable-graymap', 'PGM - Portable Graymap'),
        ('image/x-portable-pixmap', 'PPM - Portable Pixelmap'),
        ('image/x-xpixmap', 'XPM - X PixMap'),
        ('text/html', 'HTML Document (Impress)') ])

def test_suite():
  return make_suite(TestHandler)
