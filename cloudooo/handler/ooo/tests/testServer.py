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

from os.path import join
import datetime
from cloudooo.tests.cloudoooTestCase import TestCase, make_suite


class TestServer(TestCase):
  """Test XmlRpc Server. Needs cloudooo server started"""

#  def ConversionScenarioList(self):
#    return [
#            # Test Convert Doc -> Odt
#            (join('data', 'test.doc'), "doc", "odt", "application/vnd.oasis."+
#            "opendocument.text"),
#            # Test export png to svg
#            (join('data', 'test.png'), "png", "svg", "image/svg+xml"),
#            # Test export docx to odt
#            (join('data', 'test.docx'), "docx", "odt", "application/vnd.oasis."+
#            "opendocument.text"),
#            # Test export python to pdf
#            (__file__, "py", "pdf", "application/pdf"),
#            # Test if send a zipfile returns a document correctly
#            (join('data', 'test.zip'), "zip", "txt", "application/zip", True),
#            # Convert compressed html to txt
#            (join('data', 'test.zip'), "zip", "txt", "text/plain"),
#            # Test export pptx to odp
#            (join('data', 'test.pptx'), "pptx", "odp", "application/vnd.oasis."+
#            "opendocument.presentation"),
#            ]

#  def testConvert(self):
#    """Convert OOofiles"""
#    self.runConversionList(self.ConversionScenarioList())

#  def FaultConversionScenarioList(self):
#    return [
#            # Test to verify if server fail when a empty string is sent
#            ('', '', ''),
#            # Try convert one document for a invalid format
#            (open(join('data', 'test.doc')).read(), 'doc', 'xyz'),
#            # Try convert one document to format not possible
#            (open(join('data', 'test.odp')).read(), 'odp', 'doc'),
#            ]

#  def testFaultConversion(self):
#    """Convert Invalid OOofiles"""
#    self.runFaultConversionList(self.FaultConversionScenarioList())

  def GetMetadataScenarioList(self):
    return [
            # Test method getFileMetadataItemList. Without data converted
            (join('data', 'testMetadata.odt'), "odt", dict(Data='', Title='clo'+
            'udooo Test', Subject='Subject Test', Description='cloudooo Comments',
            Type='Text', MIMEType='application/vnd.oasis.opendocument.text',
            ModifyDate='2/8/2010 9:57:3', Keywords='Keywords Test')),
#            # Test method getFileMetadataItemList. With data converted
#            (join('data', 'testMetadata.odt'), "odt", dict(Title='cloudooo Test',
#            Subject='Subject Test', Description='cloudooo Comments',
#            Type='Text', MIMEType='application/vnd.oasis.opendocument.text',
#            ModifyDate='2/8/2010 9:57:3', Keywords='Keywords Test'), 
#            True),
            ]

  def testGetMetadata(self):
    """test if OOo metadata are extracted correctly"""
    self.runGetMetadataList(self.GetMetadataScenarioList())

  def UpdateMetadataScenarioList(self):
    return [
            # Test server using method updateFileMetadata
            (join('data', 'testMetadata.odt'), "odt", dict(Title='testSetMetadata')),
            # Test server using method updateFileMetadata with unsual metadata
#            (join('data', 'testMetadata.odt'), "odt", dict(Reference='testSet'+
#            'Metadata')),
#            # Test document that already has metadata. Check if the metadata is
#            # not deleted, but updated
#            (join('data', 'testMetadata.odt'), "odt", dict(Title='cloudooo Title')),
            ]

  def testUpdateMetadata(self):
    """test if OOo metadata are insert correctly"""
    self.runUpdateMetadataList(self.UpdateMetadataScenarioList())


#  def testupdateFileMetadataUpdateSomeMetadata(self):
#    """Test server using method updateFileMetadata when the same metadata is
#    updated"""
#    document_output_url = join(self.tmp_url, "testSetMetadata.odt")
#    data = open(join('data', 'testMetadata.odt'), 'r').read()
#    odf_data = self.proxy.updateFileMetadata(encodestring(data), 'odt',
#                        {"Reference": "testSetMetadata", "Something": "ABC"})
#    new_odf_data = self.proxy.updateFileMetadata(odf_data, 'odt',
#                        {"Reference": "new value", "Something": "ABC"})
#    open(document_output_url, 'w').write(decodestring(new_odf_data))
#    content_type = self._getFileType(document_output_url)
#    self.assertEquals(content_type, 'application/vnd.oasis.opendocument.text')
#    metadata_dict = self.proxy.getFileMetadataItemList(new_odf_data, 'odt')
#    self.assertEquals(metadata_dict.get("Reference"), "new value")
#    self.assertEquals(metadata_dict.get("Something"), "ABC")


#    # XXX Duplicated list of filters
#    self.text_expected_list = [['doc', 'Microsoft Word 6.0'],
#        ['doc', 'Microsoft Word 95'],
#        ['doc', 'Microsoft Word 97/2000/XP'],
#        ['docx', 'Microsoft Word 2007 XML'],
#        ['docx', 'Office Open XML Text'],
#        ['htm', 'HTML Document (OpenOffice.org Writer)'],
#        ['html', 'HTML Document (OpenOffice.org Writer)'],
#        ['html', 'XHTML'], ['odt', 'ODF Text Document'],
#        ['ott', 'ODF Text Document Template'],
#        ['pdf', 'PDF - Portable Document Format'],
#        ['rtf', 'Rich Text Format'], ['sdw', 'StarWriter 3.0'],
#        ['sdw', 'StarWriter 4.0'], ['sdw', 'StarWriter 5.0'],
#        ['sxw', 'OpenOffice.org 1.0 Text Document'],
#        ['txt', 'Text'], ['txt', 'Text Encoded'],
#        ['xhtml', 'XHTML'], ['pdb', 'AportisDoc (Palm)'],
#        ['psw', 'Pocket Word']]

#    self.text_expected_list.sort()

#    self.presentation_expected_list = [['bmp', 'BMP - Windows Bitmap'],
#        ['emf', 'EMF - Enhanced Metafile'],
#        ['eps', 'EPS - Encapsulated PostScript'],
#        ['gif', 'GIF - Graphics Interchange Format'],
#        ['htm', 'HTML Document (OpenOffice.org Impress)'],
#        ['html', 'HTML Document (OpenOffice.org Impress)'],
#        ['html', 'XHTML'], ['jfif', 'JPEG - Joint Photographic Experts Group'],
#        ['jif', 'JPEG - Joint Photographic Experts Group'],
#        ['jpe', 'JPEG - Joint Photographic Experts Group'],
#        ['jpeg', 'JPEG - Joint Photographic Experts Group'],
#        ['jpg', 'JPEG - Joint Photographic Experts Group'],
#        ['met', 'MET - OS/2 Metafile'], ['odg', 'ODF Drawing (Impress)'],
#        ['odp', 'ODF Presentation'],
#        ['otp', 'ODF Presentation Template'],
#        ['pbm', 'PBM - Portable Bitmap'], ['pct', 'PCT - Mac Pict'],
#        ['pdf', 'PDF - Portable Document Format'],
#        ['pgm', 'PGM - Portable Graymap'], ['pict', 'PCT - Mac Pict'],
#        ['png', 'PNG - Portable Network Graphic'],
#        ['pot', 'Microsoft PowerPoint 97/2000/XP Template'],
#        ['ppm', 'PPM - Portable Pixelmap'],
#        ['pps', 'Microsoft PowerPoint 97/2000/XP'],
#        ['ppt', 'Microsoft PowerPoint 97/2000/XP'],
#        ['ras', 'RAS - Sun Raster Image'],
#        ['sda', 'StarDraw 5.0 (OpenOffice.org Impress)'],
#        ['sdd', 'StarDraw 3.0 (OpenOffice.org Impress)'],
#        ['sdd', 'StarImpress 4.0'], ['sdd', 'StarImpress 5.0'],
#        ['svg', 'SVG - Scalable Vector Graphics'],
#        ['svm', 'SVM - StarView Metafile'],
#        ['sxd', 'OpenOffice.org 1.0 Drawing (OpenOffice.org Impress)'],
#        ['sxi', 'OpenOffice.org 1.0 Presentation'],
#        ['tif', 'TIFF - Tagged Image File Format'],
#        ['tiff', 'TIFF - Tagged Image File Format'],
#        ['wmf', 'WMF - Windows Metafile'],
#        ['xhtml', 'XHTML'], ['xpm', 'XPM - X PixMap']]

#    self.presentation_expected_list.sort()

#  def testGetAllowedExtensionListByType(self):
#    """Call getAllowedExtensionList and verify if the returns is a list with
#    extension and ui_name. The request is by document type"""
#    text_request = {'document_type': "text"}
#    text_allowed_list = self.proxy.getAllowedExtensionList(text_request)
#    text_allowed_list.sort()
#    for arg in text_allowed_list:
#      self.assertTrue(arg in self.text_expected_list,
#                    "%s not in %s" % (arg, self.text_expected_list))
#    request_dict = {'document_type': "presentation"}
#    presentation_allowed_list = self.proxy.getAllowedExtensionList(request_dict)
#    presentation_allowed_list.sort()
#    for arg in presentation_allowed_list:
#      self.assertTrue(arg in self.presentation_expected_list,
#                    "%s not in %s" % (arg, self.presentation_expected_list))

#  def testGetAllowedExtensionListByExtension(self):
#    """Call getAllowedExtensionList and verify if the returns is a list with
#    extension and ui_name. The request is by extension"""
#    doc_allowed_list = self.proxy.getAllowedExtensionList({'extension': "doc"})
#    doc_allowed_list.sort()
#    for arg in doc_allowed_list:
#      self.assertTrue(arg in self.text_expected_list,
#                    "%s not in %s" % (arg, self.text_expected_list))

#  def testGetAllowedExtensionListByMimetype(self):
#    """Call getAllowedExtensionList and verify if the returns is a list with
#    extension and ui_name. The request is by mimetype"""
#    request_dict = {"mimetype": "application/msword"}
#    msword_allowed_list = self.proxy.getAllowedExtensionList(request_dict)
#    msword_allowed_list.sort()
#    for arg in msword_allowed_list:
#      self.assertTrue(arg in self.text_expected_list,
#                    "%s not in %s" % (arg, self.text_expected_list))

#  def testRunConvertMethod(self):
#    """Test run_convert method"""
#    data = open(join('data', 'test.doc'), 'r').read()
#    response_code, response_dict, response_message = \
#              self.proxy.run_convert('test.doc', encodestring(data))
#    self.assertEquals(response_code, 200)
#    self.assertEquals(type(response_dict), DictType)
#    self.assertNotEquals(response_dict['data'], '')
#    self.assertEquals(sorted(response_dict.keys()),
#                              ['data', 'meta', 'mime'])
#    self.assertEquals(response_message, '')
#    self.assertEquals(response_dict['meta']['MIMEType'],
#                              'application/vnd.oasis.opendocument.text')

#  def testRunConvertFailResponse(self):
#    """Test run_convert method with invalid file"""
#    data = open(join('data', 'test.doc'), 'r').read()[:30]
#    response_code, response_dict, response_message = \
#              self.proxy.run_convert('test.doc', encodestring(data))
#    self.assertEquals(response_code, 402)
#    self.assertEquals(type(response_dict), DictType)
#    self.assertEquals(response_dict, {})
#    msg = "This document can not be loaded or is empty\n"
#    self.assertTrue(response_message.endswith(msg),
#                    "%s != %s" % (response_message, msg))

#  def testRunGenerateMethod(self):
#    """Test run_generate method"""
#    data = open(join('data', 'test.odt'), 'r').read()
#    generate_result = self.proxy.run_generate('test.odt',
#                                      encodestring(data),
#                                      None, 'pdf',
#                                      'application/vnd.oasis.opendocument.text')
#    response_code, response_dict, response_message = generate_result
#    self.assertEquals(response_code, 200)
#    self.assertEquals(type(response_dict), DictType)
#    self.assertNotEquals(response_dict['data'], '')
#    self.assertEquals(response_dict['mime'], 'application/pdf')

#  def testRunGenerateMethodConvertOdsToHTML(self):
#    """Test run_generate method. This test is to validate a bug convertions to
#    html"""
#    data = open(join('data', 'test.ods'), 'r').read()
#    generate_result = self.proxy.run_generate('test.ods',
#                                      encodestring(data),
#                                      None, 'html',
#                                      "application/vnd.oasis.opendocument.spreadsheet")
#    response_code, response_dict, response_message = generate_result
#    self.assertEquals(response_code, 200)
#    self.assertEquals(type(response_dict), DictType)
#    self.assertNotEquals(response_dict['data'], '')
#    self.assertEquals(response_dict['mime'], 'application/zip')
#    output_url = join(self.tmp_url, "zip.zip")
#    open(output_url, 'w').write(decodestring(response_dict['data']))
#    self.assertTrue(is_zipfile(output_url))
#    filename_list = [file.filename for file in ZipFile(output_url).filelist]
#    for filename in filename_list:
#      if filename.endswith("impr.html"):
#        break
#    else:
#      self.fail("Not exists one file with 'impr.html' format")
#    if exists(output_url):
#      remove(output_url)

#  def testPNGFileToConvertOdpToHTML(self):
#    """Test run_generate method. This test if returns good png files"""
#    data = open(join('data', 'test_png.odp'), 'r').read()
#    generate_result = self.proxy.run_generate('test_png.odp',
#                                      encodestring(data),
#                                      None, 'html',
#                                      'application/vnd.oasis.opendocument.presentation')
#    response_code, response_dict, response_message = generate_result
#    self.assertEquals(response_code, 200)
#    self.assertEquals(type(response_dict), DictType)
#    self.assertNotEquals(response_dict['data'], '')
#    self.assertEquals(response_dict['mime'], 'application/zip')
#    output_url = join(self.tmp_url, "zip.zip")
#    open(output_url, 'w').write(decodestring(response_dict['data']))
#    self.assertTrue(is_zipfile(output_url))
#    zipfile = ZipFile(output_url)
#    try:
#      png_path = join(self.tmp_url, "img0.png")
#      zipfile.extractall(self.tmp_url)
#      content_type = self._getFileType(png_path)
#      self.assertEquals(content_type, 'image/png')
#      m = magic.Magic()
#      self.assertTrue("8-bit/color RGB" in m.from_file(png_path))
#    finally:
#      zipfile.close()
#    if exists(output_url):
#      remove(output_url)

#  def testRunGenerateMethodConvertOdpToHTML(self):
#    """Test run_generate method. This test is to validate a bug convertions to
#    html"""
#    data = open(join('data', 'test.odp'), 'r').read()
#    generate_result = self.proxy.run_generate('test.odp',
#                                      encodestring(data),
#                                      None, 'html',
#                                      'application/vnd.oasis.opendocument.presentation')
#    response_code, response_dict, response_message = generate_result
#    self.assertEquals(response_code, 200)
#    self.assertEquals(type(response_dict), DictType)
#    self.assertNotEquals(response_dict['data'], '')
#    self.assertEquals(response_dict['mime'], 'application/zip')
#    output_url = join(self.tmp_url, "zip.zip")
#    open(output_url, 'w').write(decodestring(response_dict['data']))
#    self.assertTrue(is_zipfile(output_url))
#    filename_list = [file.filename for file in ZipFile(output_url).filelist]
#    for filename in filename_list:
#      if filename.endswith("impr.html"):
#        break
#    else:
#      self.fail("Not exists one file with 'impr.html' format")

#  # XXX disable this test because LibreOffice 3.3 can open such a broken
#  # document.
#  def _testRunGenerateMethodFailResponse(self):
#    """Test run_generate method with invalid document"""
#    data = open(join('data', 'test.odt'), 'r').read()[:100]
#    generate_result = self.proxy.run_generate('test.odt',
#                                      encodestring(data),
#                                      None, 'pdf', 'application/vnd.oasis.opendocument.text')
#    response_code, response_dict, response_message = generate_result
#    self.assertEquals(response_code, 402)
#    self.assertEquals(type(response_dict), DictType)
#    self.assertEquals(response_dict, {})
#    self.assertTrue(response_message.startswith('Traceback'))

#  def testRunSetMetadata(self):
#    """Test run_setmetadata method"""
#    data = open(join('data', 'testMetadata.odt'), 'r').read()
#    setmetadata_result = self.proxy.run_setmetadata('testMetadata.odt',
#                          encodestring(data),
#                          {"Title": "testSetMetadata", "Description": "Music"})
#    response_code, response_dict, response_message = setmetadata_result
#    self.assertEquals(response_code, 200)
#    self.assertNotEquals(response_dict['data'], '')
#    getmetadata_result = self.proxy.run_getmetadata('testMetadata.odt',
#                                                  response_dict['data'])
#    response_code, response_dict, response_message = getmetadata_result
#    self.assertEquals(response_code, 200)
#    self.assertEquals(response_dict['meta']['MIMEType'],
#                      'application/vnd.oasis.opendocument.text')
#    self.assertEquals(response_dict['meta']['Description'], "Music")
#    setmetadata_result = self.proxy.run_setmetadata('testMetadata.odt',
#                          encodestring(data),
#                          {"Title": "Namie's working record",
#                           "Description": "Music"})
#    response_code, response_dict, response_message = setmetadata_result
#    getmetadata_result = self.proxy.run_getmetadata('testMetadata.odt',
#                                                  response_dict['data'])
#    response_code, response_dict, response_message = getmetadata_result
#    self.assertEquals(response_code, 200)
#    self.assertEquals(response_dict['meta']['title'],
#                      "Namie's working record")

#  def testRunSetMetadataFailResponse(self):
#    """Test run_setmetadata method with invalid document"""
#    data = open(join('data', 'testMetadata.odt'), 'r').read()[:100]
#    setmetadata_result = self.proxy.run_setmetadata('testMetadata.odt',
#                          encodestring(data),
#                          {"Title": "testSetMetadata", "Description": "Music"})
#    response_code, response_dict, response_message = setmetadata_result
#    self.assertEquals(response_code, 402)
#    self.assertEquals(response_dict, {})
#    self.assertTrue(response_message.startswith('Traceback'))

#  def testGetAllowedTargetItemList(self):
#    """Test if filter name returns correctly with ERP5 API"""
#    mimetype = 'application/vnd.oasis.opendocument.text'
#    response_code, response_dict, response_message = \
#                  self.proxy.getAllowedTargetItemList(mimetype)
#    self.assertEquals(response_code, 200)
#    self.assertEquals(len(response_dict['response_data']), 17)
#    self.assertTrue(['html', 'HTML Document (OpenOffice.org Writer)'] in response_dict['response_data'])
#    self.assertFalse(['html', 'HTML Document'] in response_dict['response_data'])

#  def testGetTableItemList(self):
#    """Test if manager can get the table item list"""
#    table_list = [['Developers', ''],
#                  ['Prices', 'Table 1: Prices table from Mon Restaurant'],
#                  ['SoccerTeams', 'Tabela 2: Soccer Teams']]
#    data = encodestring(open("data/granulate_table_test.odt").read())
#    granulated_table = self.proxy.getTableItemList(data, "odt")
#    self.assertEquals(table_list, granulated_table)
#    #.doc
#    table_list = [['Table1', ''],
#                  ['Table2', 'Table 1: Prices table from Mon Restaurant'],
#                  ['Table3', 'Tabela 2: Soccer Teams']]
#    data = encodestring(open("data/granulate_table_test.doc").read())
#    granulated_table = self.proxy.getTableItemList(data, "doc")
#    self.assertEquals(table_list, granulated_table)

#  def testGetTable(self):
#    """Test if manager can get a item of some granulated table"""
#    data = encodestring(open("./data/granulate_table_test.odt").read())
#    granulated_table = self.proxy.getTableItemList(data, "odt")
#    table_item = decodestring(self.proxy.getTable(data, granulated_table[1][0],
#                                                      "odt"))
#    content_xml_str = ZipFile(StringIO(table_item)).read('content.xml')
#    content_xml = etree.fromstring(content_xml_str)
#    table_list = content_xml.xpath('//table:table',
#                                   namespaces=content_xml.nsmap)
#    self.assertEquals(1, len(table_list))
#    table = table_list[0]
#    name_key = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name'
#    self.assertEquals(granulated_table[1][0], table.attrib[name_key])
#    #.doc
#    data = encodestring(open("./data/granulate_table_test.doc").read())
#    granulated_table = self.proxy.getTableItemList(data, "doc")
#    self.proxy.getTable(data, granulated_table[1][0], "doc")
#    table_item = decodestring(self.proxy.getTable(data, granulated_table[1][0],
#                                                      "doc"))
#    content_xml_str = ZipFile(StringIO(table_item)).read('content.xml')
#    content_xml = etree.fromstring(content_xml_str)
#    table_list = content_xml.xpath('//table:table',
#                                   namespaces=content_xml.nsmap)
#    self.assertEquals(1, len(table_list))
#    table = table_list[0]
#    name_key = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name'
#    self.assertEquals(granulated_table[1][0], table.attrib[name_key])

#  def testGetColumnItemList(self):
#    """Test if manager can get the list of column item"""
#    data = encodestring(open("./data/granulate_table_test.odt").read())
#    columns = self.proxy.getColumnItemList(data, "SoccerTeams", "odt")
#    self.assertEquals([[0, 'Name'], [1, 'Country']], columns)
#    #.doc
#    data = encodestring(open("./data/granulate_table_test.doc").read())
#    #in the doc format the tables lose their names
#    columns = self.proxy.getColumnItemList(data, "Table3", "doc")
#    self.assertEquals([[0, 'Name'], [1, 'Country']], columns)

#  def testGetLineItemList(self):
#    """Test if manager can get the list of lines items"""
#    data = encodestring(open("./data/granulate_table_test.odt").read())
#    line_item_list = self.proxy.getLineItemList(data, "Developers", "odt")
#    self.assertEquals([['Name', 'Hugo'], ['Phone', '+55 (22) 8888-8888'],
#                       ['Email', 'hugomaia@tiolive.com'], ['Name', 'Rafael'],
#                       ['Phone', '+55 (22) 9999-9999'],
#                       ['Email', 'rafael@tiolive.com']], line_item_list)
#    #.doc
#    data = encodestring(open("./data/granulate_table_test.doc").read())
#    line_item_list = self.proxy.getLineItemList(data, "Table1", "doc")
#    self.assertEquals([['Name', 'Hugo'], ['Phone', '+55 (22) 8888-8888'],
#                       ['Email', 'hugomaia@tiolive.com'], ['Name', 'Rafael'],
#                       ['Phone', '+55 (22) 9999-9999'],
#                       ['Email', 'rafael@tiolive.com']], line_item_list)

#  def testGetImageItemList(self):
#    """Test if manager can get the list of images items"""
#    data = encodestring(open("./data/granulate_test.odt").read())
#    image_list = self.proxy.getImageItemList(data, "odt")
#    self.assertEquals([['10000000000000C80000009C38276C51.jpg', ''],
#                      ['10000201000000C80000004E7B947D46.png', 'TioLive Logo'],
#                      ['10000201000000C80000004E7B947D46.png', ''],
#                      ['2000004F00004233000013707E7DE37A.svm', 'Python Logo'],
#                      ['10000201000000C80000004E7B947D46.png',
#                                                        'Again TioLive Logo']],
#                                                                    image_list)
#    #.doc
#    data = encodestring(open("./data/granulate_test.doc").read())
#    image_list = self.proxy.getImageItemList(data, "doc")
#    self.assertEquals([['10000000000000C80000009C38276C51.jpg', ''],
#                      ['10000201000000C80000004E7B947D46.png', 'TioLive Logo'],
#                      ['10000201000000C80000004E7B947D46.png', ''],
#                      ['200003160000423300001370F468B63D.wmf', 'Python Logo'],
#                      ['10000201000000C80000004E7B947D46.png',
#                                                        'Again TioLive Logo']],
#                                                                    image_list)

#  def testGetImage(self):
#    """Test if manager can get a image"""
#    data = encodestring(open("./data/granulate_test.odt").read())
#    zip = ZipFile(StringIO(decodestring(data)))
#    image_id = '10000000000000C80000009C38276C51.jpg'
#    original_image = zip.read('Pictures/%s' % image_id)
#    geted_image = decodestring(self.proxy.getImage(data, image_id, "odt"))
#    self.assertEquals(original_image, geted_image)
#    #.doc
#    data = encodestring(open("./data/granulate_test.doc").read())
#    #This conversion is necessary to catch the image from the doc file;
#    #so compare with the server return.
#    data_odt = self.proxy.convertFile(data, 'doc', 'odt', False)
#    zip = ZipFile(StringIO(decodestring(data_odt)))
#    image_id = '10000000000000C80000009C38276C51.jpg'
#    original_image = zip.read('Pictures/%s' % image_id)
#    geted_image = decodestring(self.proxy.getImage(data, image_id, "doc"))
#    self.assertEquals(original_image, geted_image)

#  def testGetParagraphItemList(self):
#    """Test if paragraphs are extracted correctly from document"""
#    data = encodestring(open("./data/granulate_test.odt").read())
#    paragraph_list = self.proxy.getParagraphItemList(data, "odt")
#    self.assertEquals([[0, 'P3'], [1, 'P1'], [2, 'P12'], [3, 'P6'], [4, 'P7'],
#                      [5, 'P8'], [6, 'P6'], [7, 'P6'], [8, 'P13'], [9, 'P9'],
#                      [10, 'P9'], [11, 'P9'], [12, 'P4'], [13, 'P10'], [14,
#                      'P5'], [15, 'P5'], [16, 'P14'], [17, 'P11'], [18, 'P11'],
#                      [19, 'Standard'], [20, 'P2'], [21, 'P2'], [22, 'P2'],
#                      [23, 'P2'], [24, 'P2'], [25, 'P2'], [26, 'P2'], [27,
#                      'P2'], [28, 'P2'], [29, 'P2']], paragraph_list)

#  def testGetParagraphItem(self):
#    """Test if manager can get a paragraph"""
#    data = encodestring(open("./data/granulate_test.odt").read())
#    paragraph = self.proxy.getParagraph(data, 1, "odt")
#    self.assertEquals(['', 'P1'], paragraph)

#  def testGetChapterItemList(self):
#    """Test if the chapters list is extracted correctly from document"""
#    data = encodestring(open("./data/granulate_chapters_test.odt").read())
#    chapter_list = self.proxy.getChapterItemList(data, "odt")
#    self.assertEquals([[0, 'Title 0'], [1, 'Title 1'], [2, 'Title 2'],
#                       [3, 'Title 3'], [4, 'Title 4'], [5, 'Title 5'],
#                       [6, 'Title 6'], [7, 'Title 7'], [8, 'Title 8'],
#                       [9, 'Title 9'], [10, 'Title 10']] , chapter_list)

#  def testGetChapterItem(self):
#    """Test if manager can get a chapter"""
#    data = encodestring(open("./data/granulate_chapters_test.odt").read())
#    chapter = self.proxy.getChapterItem(1, data, "odt")
#    self.assertEquals(['Title 1', 1], chapter)

def test_suite():
  return make_suite(TestServer)
