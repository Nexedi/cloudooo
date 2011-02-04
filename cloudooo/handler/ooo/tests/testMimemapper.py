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

from cloudoooTestCase import CloudoooTestCase
from cloudooo.handler.ooo.application.openoffice import openoffice
from cloudooo.handler.ooo.mimemapper import MimeMapper
from cloudoooTestCase import make_suite

text_expected_tuple = (
    ('doc', 'Microsoft Word 6.0'),
    ('doc', 'Microsoft Word 95'),
    ('doc', 'Microsoft Word 97/2000/XP'),
    ('docx', 'Microsoft Word 2007 XML'),
    ('docx', 'Office Open XML Text'),
    ('html', 'HTML Document (OpenOffice.org Writer)'),
    ('html', 'XHTML'),
    ('odt', 'ODF Text Document'),
    ('ott', 'ODF Text Document Template'),
    ('pdf', 'PDF - Portable Document Format'),
    ('rtf', 'Rich Text Format'),
    ('sdw', 'StarWriter 3.0'),
    ('sdw', 'StarWriter 4.0'),
    ('sdw', 'StarWriter 5.0'),
    ('sxw', 'OpenOffice.org 1.0 Text Document'),
    ('txt', 'Text Encoded'),
    ('txt', 'Text'),
    ('pdb', 'AportisDoc (Palm)'),
    ('psw', 'Pocket Word'),
    )

global_expected_tuple = (
    )

drawing_expected_tuple = (
    ('bmp', 'BMP - Windows Bitmap'),
    ('emf', 'EMF - Enhanced Metafile'),
    ('eps', 'EPS - Encapsulated PostScript'),
    ('gif', 'GIF - Graphics Interchange Format'),
    ('html', 'HTML Document (OpenOffice.org Draw)'),
    ('html', 'XHTML'),
    ('jpg', 'JPEG - Joint Photographic Experts Group'),
    ('met', 'MET - OS/2 Metafile'),
    ('odg', 'ODF Drawing'),
    ('otg', 'ODF Drawing Template'),
    ('pbm', 'PBM - Portable Bitmap'),
    ('pct', 'PCT - Mac Pict'),
    ('pdf', 'PDF - Portable Document Format'),
    ('pgm', 'PGM - Portable Graymap'),
    ('png', 'PNG - Portable Network Graphic'),
    ('ppm', 'PPM - Portable Pixelmap'),
    ('ras', 'RAS - Sun Raster Image'),
    ('sda', 'StarDraw 5.0'),
    ('sdd', 'StarDraw 3.0'),
    ('svg', 'SVG - Scalable Vector Graphics'),
    ('svm', 'SVM - StarView Metafile'),
    ('sxd', 'OpenOffice.org 1.0 Drawing'),
    ('tif', 'TIFF - Tagged Image File Format'),
    ('wmf', 'WMF - Windows Metafile'),
    ('xpm', 'XPM - X PixMap'),
    )

web_expected_tuple = (
    ('html', 'HTML Document'),
    ('odt', 'OpenOffice.org Text (OpenOffice.org Writer/Web)'),
    ('pdf', 'PDF - Portable Document Format'),
    ('sdw', 'StarWriter 3.0 (OpenOffice.org Writer/Web)'),
    ('sdw', 'StarWriter 4.0 (OpenOffice.org Writer/Web)'),
    ('sdw', 'StarWriter 5.0 (OpenOffice.org Writer/Web)'),
    ('sxw', 'OpenOffice.org 1.0 Text Document (OpenOffice.org Writer/Web)'),
    ('txt', 'Text (OpenOffice.org Writer/Web)'),
    ('txt', 'Text Encoded (OpenOffice.org Writer/Web)'),
    )

presentation_expected_tuple = (
    ('bmp', 'BMP - Windows Bitmap'),
    ('emf', 'EMF - Enhanced Metafile'),
    ('eps', 'EPS - Encapsulated PostScript'),
    ('gif', 'GIF - Graphics Interchange Format'),
    ('html', 'HTML Document (OpenOffice.org Impress)'),
    ('html', 'XHTML'),
    ('jpg', 'JPEG - Joint Photographic Experts Group'),
    ('met', 'MET - OS/2 Metafile'),
    ('odg', 'ODF Drawing (Impress)'),
    ('odp', 'ODF Presentation'),
    ('otp', 'ODF Presentation Template'),
    ('pbm', 'PBM - Portable Bitmap'),
    ('pct', 'PCT - Mac Pict'),
    ('pdf', 'PDF - Portable Document Format'),
    ('pgm', 'PGM - Portable Graymap'),
    ('png', 'PNG - Portable Network Graphic'),
    ('pot', 'Microsoft PowerPoint 97/2000/XP Template'),
    ('ppm', 'PPM - Portable Pixelmap'),
    ('pps', 'Microsoft PowerPoint 97/2000/XP'),
    ('ppt', 'Microsoft PowerPoint 97/2000/XP'),
    ('ras', 'RAS - Sun Raster Image'),
    ('sda', 'StarDraw 5.0 (OpenOffice.org Impress)'),
    ('sdd', 'StarDraw 3.0 (OpenOffice.org Impress)'),
    ('sdd', 'StarImpress 4.0'), ('sdd', 'StarImpress 5.0'),
    ('svg', 'SVG - Scalable Vector Graphics'),
    ('svm', 'SVM - StarView Metafile'),
    ('sxd', 'OpenOffice.org 1.0 Drawing (OpenOffice.org Impress)'),
    ('sxi', 'OpenOffice.org 1.0 Presentation'),
    ('tif', 'TIFF - Tagged Image File Format'),
    ('wmf', 'WMF - Windows Metafile'),
    ('xpm', 'XPM - X PixMap'),
    )

spreadsheet_expected_list = (
    ('csv', 'Text CSV'),
    ('html', 'HTML Document (OpenOffice.org Calc)'),
    ('html', 'XHTML'),
    ('ods', 'ODF Spreadsheet'),
    ('ots', 'ODF Spreadsheet Template'),
    ('pdf', 'PDF - Portable Document Format'),
    ('sdc', 'StarCalc 3.0'),
    ('sdc', 'StarCalc 4.0'),
    ('sdc', 'StarCalc 5.0'),
    ('sxc', 'OpenOffice.org 1.0 Spreadsheet'),
    ('xls', 'Microsoft Excel 5.0'),
    ('xls', 'Microsoft Excel 95'),
    ('xls', 'Microsoft Excel 97/2000/XP'),
    ('xlt', 'Microsoft Excel 5.0 Template'),
    ('xlt', 'Microsoft Excel 95 Template'),
    ('xlt', 'Microsoft Excel 97/2000/XP Template'),
    )

math_expected_tuple = (
    ('mml', 'MathML 1.01'),
    ('odf', 'ODF Formula'),
    ('pdf', 'PDF - Portable Document Format'),
    ('smf', 'StarMath 3.0'),
    ('smf', 'StarMath 4.0'),
    ('smf', 'StarMath 5.0'),
    ('sxm', 'OpenOffice.org 1.0 Formula'),
    )

chart_expected_tuple = (
    )

OPENOFFICE = True

class TestMimeMapper(CloudoooTestCase):
  """Test if object load filters correctly of OOo."""

  def afterSetUp(self):
    """Mimemapper is created and load uno path."""
    self.mimemapper = MimeMapper()
    openoffice.acquire()
    hostname, port = openoffice.getAddress()
    self.mimemapper.loadFilterList(hostname,
                                  port,
                                  python_path=self.python_path)
    openoffice.release()

  def testGetFilterWhenExtensionNotExist(self):
    """Test the case that the user passes extension which does not exist."""
    empty_list = self.mimemapper.getFilterList('xxx')
    self.assertEquals(empty_list, [])

  def testIfThereIsDuplicateData(self):
    """Test if there is duplicate data."""
    # XXX It can not exists multiple keys inside a dictionary
    extension_list = self.mimemapper._doc_type_list_by_extension.keys()
    self.assertEquals(len(extension_list), len(set(extension_list)))
    for type_list in self.mimemapper._doc_type_list_by_extension.values():
      self.assertEquals(len(type_list), len(set(type_list)))
    document_type_list = self.mimemapper._document_type_dict.keys()
    self.assertEquals(len(document_type_list), len(set(document_type_list)))
    document_service_list = self.mimemapper._document_type_dict.values()
    self.assertEquals(len(document_service_list), len(set(document_service_list)))
    document_service_list = self.mimemapper._extension_list_by_type.keys()
    self.assertEquals(len(document_service_list), len(set(document_service_list)))
    extension_list = self.mimemapper._extension_list_by_type.values()
    for extension in extension_list:
      self.assertEquals(len(extension), len(set(extension)),
          "extension_list_by_type has duplicate data")

  def testGetFilterByExt(self):
    """Test if passing the extension the filter returns corretcly."""
    pdf_filter_list = self.mimemapper.getFilterList('pdf')
    self.assertEquals(len(pdf_filter_list), 5)
    xls_filter_list = self.mimemapper.getFilterList('xls')
    self.assertEquals(len(xls_filter_list), 3)
    doc_filter_list = self.mimemapper.getFilterList('doc')
    self.assertEquals(len(doc_filter_list), 3)

  def testGetDocumentTypeDict(self):
    """Test if dictonary document type returns type correctly."""
    document_type_dict = self.mimemapper._document_type_dict
    type = document_type_dict.get("text")
    self.assertEquals(type, 'com.sun.star.text.TextDocument')
    type = document_type_dict.get("chart")
    # For now, chart document filters are maked as NotInFileDialog and
    # NotInChooser.
    # self.assertEquals(type, 'com.sun.star.chart2.ChartDocument')
    self.assertEquals(type, None)
    type = document_type_dict.get("drawing")
    self.assertEquals(type, 'com.sun.star.drawing.DrawingDocument')
    type = document_type_dict.get("presentation")
    self.assertEquals(type, 'com.sun.star.presentation.PresentationDocument')
    type = document_type_dict.get("spreadsheet")
    self.assertEquals(type, 'com.sun.star.sheet.SpreadsheetDocument')
    type = document_type_dict.get("web")
    self.assertEquals(type, 'com.sun.star.text.WebDocument')

  def testGetAllowedExtensionListByExtension(self):
    """Test if function getAllowedExtensionList returns correctly a list with
    extensions that can generate with extension passed."""
    doc_got_list = list(self.mimemapper.getAllowedExtensionList('doc'))
    for arg in doc_got_list:
      self.assertTrue(arg in text_expected_tuple,
              "%s not in %s" % (arg, text_expected_tuple))
    jpeg_got_list = list(self.mimemapper.getAllowedExtensionList('jpeg'))
    jpeg_expected_list = list(set(presentation_expected_tuple +
        drawing_expected_tuple))
    for arg in jpeg_got_list:
      self.assertTrue(arg in jpeg_expected_list,
              "%s not in %s" % (arg, jpeg_expected_list))
    pdf_got_list = list(self.mimemapper.getAllowedExtensionList('pdf'))
    pdf_expected_list = list(set(presentation_expected_tuple +
      drawing_expected_tuple + web_expected_tuple + global_expected_tuple +
      math_expected_tuple + text_expected_tuple + spreadsheet_expected_list))
    for arg in pdf_got_list:
      self.assertTrue(arg in pdf_expected_list,
              "%s not in %s" % (arg, pdf_expected_list))

  def testGetAllowedExtensionListForText(self):
    """Passing document_type equal to 'text', the return must be equal
    to text_expected_tuple."""
    got_list = list(self.mimemapper.getAllowedExtensionList(document_type='text'))
    text_expected_list = list(text_expected_tuple)
    for arg in got_list:
      self.assertTrue(arg in text_expected_list,
              "%s not in %s" % (arg, text_expected_list))

  def testGetAllowedExtensionListForGlobal(self):
    """Passing document_type equal to 'global', the return must be equal
    to global_expected_tuple."""
    got_list = list(self.mimemapper.getAllowedExtensionList(document_type='global'))
    got_list.sort()
    global_expected_list = list(global_expected_tuple)
    global_expected_list.sort()
    self.assertEquals(got_list, global_expected_list)

  def testGetAllAllowedExtensionListForDrawing(self):
    """Passing document_type equal to 'drawing', the return must be equal
    to drawing_expected_tuple."""
    got_list = list(self.mimemapper.getAllowedExtensionList(document_type='drawing'))
    drawing_expected_list = list(drawing_expected_tuple)
    drawing_expected_list.sort()
    for arg in got_list:
      self.assertTrue(arg in drawing_expected_list,
          "%s not in %s" % (arg, drawing_expected_list))

  def testGetAllAllowedExtensionListForWeb(self):
    """Passing document_type equal to 'web', the return must be equal
    to web_expected_tuple."""
    got_tuple = list(self.mimemapper.getAllowedExtensionList(document_type='web'))
    got_tuple.sort()
    web_expected_list = list(web_expected_tuple)
    web_expected_list.sort()
    self.assertEquals(got_tuple, web_expected_list)

  def testGetAllAllowedExtensionListForPresentation(self):
    """Passing document_type equal to 'presentation', the return must be equal
    to presentation_expected_tuple."""
    got_list = \
        list(self.mimemapper.getAllowedExtensionList(document_type='presentation'))
    presentation_expected_list = list(presentation_expected_tuple)
    presentation_expected_list.sort()
    for arg in got_list:
      self.assertTrue(arg in presentation_expected_list,
          "%s not in %s" % (arg, presentation_expected_list))

  def testGetAllAllowedExtensionListForSpreadsheet(self):
    """Passing document_type equal to 'spreadsheet', the return must be equal
    to spreadsheet_expected_list."""
    got_list = self.mimemapper.getAllowedExtensionList(document_type='spreadsheet')
    for arg in got_list:
      self.assertTrue(arg in spreadsheet_expected_list,
          "%s not in %s" % (arg, spreadsheet_expected_list))

  def testGetAllAllowedExtensionListForChart(self):
    """Passing document_type equal to 'chart', the return must be equal
    to chart_expected_tuple."""
    got_list = list(self.mimemapper.getAllowedExtensionList(document_type='chart'))
    got_list.sort()
    chart_expected_list = list(chart_expected_tuple)
    chart_expected_list.sort()
    self.assertEquals(got_list, chart_expected_list)

  def testGetFilterName(self):
    """Test if passing extension and document_type, the filter is correct."""
    filtername = self.mimemapper.getFilterName("xls",
                                            'com.sun.star.sheet.SpreadsheetDocument')
    self.assertEquals(filtername, "MS Excel 97")
    filtername = self.mimemapper.getFilterName("sxw",
                                            'com.sun.star.text.TextDocument')
    self.assertEquals(filtername, "StarOffice XML (Writer)")
    filtername = self.mimemapper.getFilterName("pdf",
                                            'com.sun.star.text.TextDocument')
    self.assertEquals(filtername, "writer_pdf_Export")
    filtername = self.mimemapper.getFilterName('ppt',
                             'com.sun.star.presentation.PresentationDocument')
    self.assertEquals(filtername, "MS PowerPoint 97")
    filtername = self.mimemapper.getFilterName("html",
                             'com.sun.star.presentation.PresentationDocument')
    self.assertEquals(filtername, "impress_html_Export")

def test_suite():
  return make_suite(TestMimeMapper)
