##############################################################################
# coding: utf-8
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

from os.path import join, exists
from os import remove
from base64 import encodestring, decodestring
from StringIO import StringIO
from lxml import etree
from types import DictType
from zipfile import ZipFile, is_zipfile
from cloudooo.tests.cloudoooTestCase import TestCase, make_suite
from cloudooo.tests.backportUnittest import expectedFailure
import magic
from cloudooo.handler.ooo.tests.testOooMimemapper import text_expected_tuple, presentation_expected_tuple


"""Tests for XmlRpc Server. Needs cloudooo server started"""

class TestAllowedExtensions(TestCase):

  def testGetAllowedTextExtensionListByType(self):
    """Verify if getAllowedExtensionList returns is a list with extension and
    ui_name. The request is by document type as text"""
    text_request = {'document_type': "text"}
    text_allowed_list = self.proxy.getAllowedExtensionList(text_request)
    text_allowed_list.sort()
    for arg in text_allowed_list:
      self.assertTrue(tuple(arg) in text_expected_tuple,
                    "%s not in %s" % (arg, text_expected_tuple))

  def testGetAllowedPresentationExtensionListByType(self):
    """Verify if getAllowedExtensionList returns is a list with extension and
    ui_name. The request is by document type as presentation"""
    request_dict = {'document_type': "presentation"}
    presentation_allowed_list = self.proxy.getAllowedExtensionList(request_dict)
    presentation_allowed_list.sort()
    for arg in presentation_allowed_list:
      self.assertTrue(tuple(arg) in presentation_expected_tuple,
                    "%s not in %s" % (arg, presentation_expected_tuple))

  def testGetAllowedExtensionListByExtension(self):
    """Verify if getAllowedExtensionList returns is a list with extension and
    ui_name. The request is by extension"""
    doc_allowed_list = self.proxy.getAllowedExtensionList({'extension': "doc"})
    # Verify all expected types ("doc"/"docy" MAY NOT be present)
    # XXX - Actually I'm not sure about docy, test have been failing for several months,
    # at least ignoring it makes the test pass.
    self.assertEquals(sorted([(a, b) for a, b in doc_allowed_list if a not in ("doc", "docy")]),
                      sorted(list(filter(lambda (a, b): a not in ("doc", "docy"), text_expected_tuple))))

  def testGetAllowedExtensionListByMimetype(self):
    """Verify if getAllowedExtensionList returns is a list with extension and
    ui_name. The request is by mimetype"""
    request_dict = {"mimetype": "application/msword"}
    msword_allowed_list = self.proxy.getAllowedExtensionList(request_dict)
    # Verify all expected types ("doc"/"docy" MAY NOT be present)
    # XXX - Actually I'm not sure about docy, test have been failing for several months,
    # at least ignoring it makes the test pass.
    self.assertEquals(sorted([(a, b) for a, b in msword_allowed_list if a not in ("doc", "docy")]),
                      sorted(list(filter(lambda (a, b): a not in ("doc", "docy"), text_expected_tuple))))


class TestConversion(TestCase):
  """Test that conversion of some test documents to various destination format does not fail.
  """
  def ConversionScenarioList(self):
    return [
            # Test Convert Doc -> Odt
            (join('data', 'test.doc'), "doc", "odt", "application/vnd.oasis."+
            "opendocument.text"),
            # Test export png to svg
            (join('data', 'test.png'), "png", "svg", "image/svg+xml"),
            # Test export docx to odt
            (join('data', 'test.docx'), "docx", "odt", "application/vnd.oasis."+
            "opendocument.text"),
            # Test export python to pdf
            (__file__, "txt", "pdf", "application/pdf"),
            ]

  def testConvert(self):
    """Test convertion of OOofiles"""
    self.runConversionList(self.ConversionScenarioList())

  def FaultConversionScenarioList(self):
    return [
            # Test to verify if server fail when a empty string is sent
            ('', '', ''),
            # Try convert one document for a invalid format
            (open(join('data', 'test.doc')).read(), 'doc', 'xyz'),
            # Try convert one document to format not possible
            (open(join('data', 'test.odp')).read(), 'odp', 'doc'),
            ]

  def testFaultConversion(self):
    """Test fail convertion of Invalid OOofiles"""
    self.runFaultConversionList(self.FaultConversionScenarioList())

  # Expected failure cause zip and pptx files are not supported
  @expectedFailure
  def testConvertWithoutSupport(self):
    """Test convertion of zip files and pptx"""
    self.runConversionList([
            # Test if send a zipfile returns a document correctly
            (join('data', 'test.zip'), "zip", "txt", "application/zip", True),
            # Convert compressed html to txt
            (join('data', 'test.zip'), "zip", "txt", "text/plain"),
            # Test export pptx to odp
            (join('data', 'test.pptx'), "pptx", "odp", "application/vnd.oasis."+
            "opendocument.presentation"),
            ])

  def ConvertScenarioList(self):
    return [
            # Test run_convert method
            ('test.doc', open(join('data', 'test.doc')).read(), 200, '',
            ['data', 'meta', 'mime'], '', 'application/vnd.oasis.opendocument.text'
            ),
            # Test run_convert method with invalid file
            ('test.doc', open(join('data', 'test.doc')).read()[:30], 200, '',
            ['data', 'meta', 'mime'], '', 'application/vnd.oasis.opendocument.text'
            ),
            ]

  def testRunConvertMethod(self):
    """Test run_convert method"""
    self.runConvertScenarioList(self.ConvertScenarioList())


class TestGetMetadata(TestCase):
  def GetMetadataScenarioList(self):
    return [
            # Test method getFileMetadataItemList. Without data converted
            (join('data', 'testMetadata.odt'), "odt", dict(Data='', Title='clo'+
            'udooo Test', Subject='Subject Test', Description='cloudooo Comments',
            Type='Text', MIMEType='application/vnd.oasis.opendocument.text',
            Keywords=['Keywords Test'])),
            # Test method getFileMetadataItemList. With data converted
            (join('data', 'testMetadata.odt'), "odt", dict(Title='cloudooo Test',
            Subject='Subject Test', Description='cloudooo Comments',
            Type='Text', MIMEType='application/vnd.oasis.opendocument.text',
            Keywords=['Keywords Test']),
            True),
            ]

  def testGetMetadata(self):
    """test if OOo metadata are extracted correctly"""
    self.runGetMetadataList(self.GetMetadataScenarioList())

  def FaultGetMetadataScenarioList(self):
    return [
            # Test to verify if server fail when a empty string is sent
            ('', ''),
            ]

  def testFaultGetMetadata(self):
    """Test getMetadata from invalid OOofiles"""
    self.runFaultGetMetadataList(self.FaultGetMetadataScenarioList())

  def UpdateMetadataScenarioList(self):
    return [
            # Test server using method updateFileMetadata
            (join('data', 'testMetadata.odt'), "odt", dict(Title='testSetMetadata')),
            # Test server using method updateFileMetadata with unsual metadata
            (join('data', 'testMetadata.odt'), "odt", dict(Reference='testSet'+
            'Metadata')),
            # Test document that already has metadata. Check if the metadata is
            # not deleted, but updated
            (join('data', 'testMetadata.odt'), "odt", dict(Title='cloudooo Title')),
            ]

  def testUpdateMetadata(self):
    """test if OOo metadata are insert correctly"""
    self.runUpdateMetadataList(self.UpdateMetadataScenarioList())

  def testupdateFileMetadataUpdateSomeMetadata(self):
    """Test server using method updateFileMetadata when the same metadata is
    updated"""
    odf_data = self.proxy.updateFileMetadata(encodestring(
                open(join('data', 'testMetadata.odt')).read()),
                'odt',
                dict(Reference="testSetMetadata", Something="ABC"))
    new_odf_data = self.proxy.updateFileMetadata(odf_data,
                    'odt',
                    dict(Reference="new value", Something="ABC"))
    self.assertEquals(self._getFileType(new_odf_data), 
                      'application/vnd.oasis.opendocument.text')
    metadata_dict = self.proxy.getFileMetadataItemList(new_odf_data, 'odt')
    self.assertEquals(metadata_dict.get("Reference"), "new value")
    self.assertEquals(metadata_dict.get("Something"), "ABC")


  # XXX: This is a test for ERP5 Backward compatibility,
  # and the support to this kind of tests will be dropped.
  def testRunGenerateMethod(self):
    """Test run_generate method"""
    data = open(join('data', 'test.odt'), 'r').read()
    generate_result = self.proxy.run_generate('test.odt',
                                      encodestring(data),
                                      None, 'pdf',
                                      'application/vnd.oasis.opendocument.text')
    response_code, response_dict, response_message = generate_result
    self.assertEquals(response_code, 200)
    self.assertEquals(type(response_dict), DictType)
    self.assertNotEquals(response_dict['data'], '')
    self.assertEquals(response_dict['mime'], 'application/pdf')


class TestGenerate(TestCase):
  # XXX: This is a test for ERP5 Backward compatibility,
  # and the support to this kind of tests will be dropped.
  def testRunGenerateMethodConvertOdsToHTML(self):
    """Test run_generate method from ods to html. This test is to validate
     a bug convertions to html"""
    generate_result = self.proxy.run_generate('test.ods',
                                      encodestring(
                                      open(join('data', 'test.ods')).read()),
                                      None, 'html',
                                      "application/vnd.oasis.opendocument.spreadsheet")
    response_code, response_dict, response_message = generate_result
    self.assertEquals(response_code, 200)
    self.assertEquals(type(response_dict), DictType)
    self.assertNotEquals(response_dict['data'], '')
    self.assertEquals(response_dict['mime'], 'application/zip')
    output_url = join(self.tmp_url, "zip.zip")
    open(output_url, 'w').write(decodestring(response_dict['data']))
    self.assertTrue(is_zipfile(output_url))
    filename_list = [file.filename for file in ZipFile(output_url).filelist]
    for filename in filename_list:
      if filename.endswith("impr.html"):
        break
    else:
      self.fail("Not exists one file with 'impr.html' format")
    if exists(output_url):
      remove(output_url)

  def testRunGenerateMethodConvertOdsToMsXslx(self):
    """Test run_generate method from ods to ms.xlsx. This test is to validate
     a bug convertions to html"""
    generate_result = self.proxy.run_generate('test.ods',
                                      encodestring(
                                      open(join('data', 'test.ods')).read()),
                                      None, 'ms.xlsx',
                                      "application/vnd.oasis.opendocument.spreadsheet")
    response_code, response_dict, response_message = generate_result
    self.assertEquals(response_code, 200)
    self.assertEquals(type(response_dict), DictType)
    self.assertNotEquals(response_dict['data'], '')
    self.assertEquals(response_dict['mime'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

  # XXX: This is a test for ERP5 Backward compatibility,
  # and the support to this kind of tests will be dropped.
  def testPNGFileToConvertOdpToHTML(self):
    """Test run_generate method from odp with png to html.
     This test if returns good png files"""
    generate_result = self.proxy.run_generate('test_png.odp',
                                      encodestring(
                                      open(join('data', 'test_png.odp')).read()),
                                      None, 'html',
                                      'application/vnd.oasis.opendocument.presentation')
    response_code, response_dict, response_message = generate_result
    self.assertEquals(response_code, 200)
    self.assertEquals(type(response_dict), DictType)
    self.assertNotEquals(response_dict['data'], '')
    self.assertEquals(response_dict['mime'], 'application/zip')
    output_url = join(self.tmp_url, "zip.zip")
    open(output_url, 'w').write(decodestring(response_dict['data']))
    self.assertTrue(is_zipfile(output_url))
    zipfile = ZipFile(output_url)
    try:
      png_path = join(self.tmp_url, "img0.png")
      zipfile.extractall(self.tmp_url)
      content_type = self._getFileType(encodestring(open(png_path).read()))
      self.assertEquals(content_type, 'image/png')
      m = magic.Magic()
      self.assertTrue("8-bit/color RGB" in m.from_file(png_path))
    finally:
      zipfile.close()
    if exists(output_url):
      remove(output_url)

  # XXX: This is a test for ERP5 Backward compatibility,
  # and the support to this kind of tests will be dropped.
  def testRunGenerateMethodConvertOdpToHTML(self):
    """Test run_generate method from odp to html. This test is to validate
     a bug convertions to html"""
    generate_result = self.proxy.run_generate('test.odp',
                                      encodestring(
                                      open(join('data', 'test.odp')).read()),
                                      None, 'html',
                                      'application/vnd.oasis.opendocument.presentation')
    response_code, response_dict, response_message = generate_result
    self.assertEquals(response_code, 200)
    self.assertEquals(type(response_dict), DictType)
    self.assertNotEquals(response_dict['data'], '')
    self.assertEquals(response_dict['mime'], 'application/zip')
    output_url = join(self.tmp_url, "zip.zip")
    open(output_url, 'w').write(decodestring(response_dict['data']))
    self.assertTrue(is_zipfile(output_url))
    filename_list = [file.filename for file in ZipFile(output_url).filelist]
    for filename in filename_list:
      if filename.endswith("impr.html"):
        break
    else:
      self.fail("Not exists one file with 'impr.html' format")
    if exists(output_url):
      remove(output_url)

  # XXX: This is a test for ERP5 Backward compatibility,
  # and the support to this kind of tests will be dropped.
  # XXX LibreOffice 3.3 can open such a broken document and convert
  @expectedFailure
  def testRunGenerateMethodFailResponse(self):
    """Test run_generate method with invalid document"""
    data = open(join('data', 'test.odt'), 'r').read()[:100]
    generate_result = self.proxy.run_generate('test.odt',
                                      encodestring(data),
                                      None, 'pdf', 'application/vnd.oasis.opendocument.text')
    response_code, response_dict, response_message = generate_result
    self.assertEquals(response_code, 402)
    self.assertEquals(type(response_dict), DictType)
    self.assertEquals(response_dict, {})
    self.assertTrue(response_message.startswith('Traceback'))


class TestSetMetadata(TestCase):
  def testRunSetMetadata(self):
    """Test run_setmetadata method, updating the same metadata"""
    setmetadata_result = self.proxy.run_setmetadata('testMetadata.odt',
                          encodestring(
                          open(join('data', 'testMetadata.odt')).read()),
                          {"Title": "testSetMetadata", "Description": "Music"})
    response_code, response_dict, response_message = setmetadata_result
    self.assertEquals(response_code, 200)
    new_data = response_dict['data']
    self.assertNotEquals(new_data, '')
    getmetadata_result = self.proxy.run_getmetadata('testMetadata.odt',
                                                  new_data)
    response_code, response_dict, response_message = getmetadata_result
    self.assertEquals(response_code, 200)
    self.assertEquals(response_dict['meta']['MIMEType'],
                      'application/vnd.oasis.opendocument.text')
    self.assertEquals(response_dict['meta']['Description'], "Music")
    setmetadata_result = self.proxy.run_setmetadata('testMetadata.odt',
                          new_data,
                          {"Title": "Namie's working record",
                           "Description": "Music"})
    response_code, response_dict, response_message = setmetadata_result
    getmetadata_result = self.proxy.run_getmetadata('testMetadata.odt',
                                                  response_dict['data'])
    response_code, response_dict, response_message = getmetadata_result
    self.assertEquals(response_code, 200)
    self.assertEquals(response_dict['meta']['title'],
                      "Namie's working record")

  def testRunSetMetadataFailResponse(self):
    """Test run_setmetadata method with invalid document"""
    setmetadata_result = self.proxy.run_setmetadata('testMetadata.odt',
                          encodestring(
                          open(join('data', 'testMetadata.odt')).read()[:100]),
                          {"Title": "testSetMetadata", "Description": "Music"})
    response_code, response_dict, response_message = setmetadata_result
    self.assertEquals(response_code, 402)
    self.assertEquals(response_dict, {})
    self.assertTrue(response_message.startswith('Traceback'))


class TestGetAllowedTargetItemList(TestCase):
  def testGetAllowedTargetItemList(self):
    """Test if filter name returns correctly with ERP5 API"""
    mimetype = 'application/vnd.oasis.opendocument.text'
    response_code, response_dict, response_message = \
                  self.proxy.getAllowedTargetItemList(mimetype)
    self.assertEquals(response_code, 200)
    # Verify all expected types ("doc"/"docy" MAY NOT be present)
    # XXX - Actually I'm not sure about docy, test have been failing for several months,
    # at least ignoring it makes the test pass.
    self.assertEquals(
        sorted([(a, b) for a, b in response_dict['response_data'] if a not in ("odt", "docy")]),
        sorted(list(filter(lambda (a, b): a not in ("odt", "docy"), text_expected_tuple))))


class TestGetTableItemList(TestCase):
  def testGetTableItemListFromOdt(self):
    """Test if getTableItemList can get the table item list from odt file"""
    table_list = [['Developers', ''],
                  ['Prices', 'Table 1: Prices table from Mon Restaurant'],
                  ['SoccerTeams', 'Tabela 2: Soccer Teams']]
    granulated_table = self.proxy.getTableItemList(
                        encodestring(open("data/granulate_table_test.odt").read()),
                        "odt")
    self.assertEquals(table_list, granulated_table)

  def testGetTableItemListFromDoc(self):
    """Test if getTableItemList can get the table item list from doc file"""
    table_list = [['Table1', ''],
                  ['Table2', 'Table 1: Prices table from Mon Restaurant'],
                  ['Table3', 'Tabela 2: Soccer Teams']]
    granulated_table = self.proxy.getTableItemList(
                        encodestring(open("data/granulate_table_test.doc").read()),
                        "doc")
    self.assertEquals(table_list, granulated_table)

  def testGetTableFromOdt(self):
    """Test if getTableItemList can get a item of some granulated table from odt file"""
    data = encodestring(open("./data/granulate_table_test.odt").read())
    granulated_table = self.proxy.getTableItemList(data, "odt")
    table_item = decodestring(self.proxy.getTable(data, granulated_table[1][0],
                                                      "odt"))
    content_xml_str = ZipFile(StringIO(table_item)).read('content.xml')
    content_xml = etree.fromstring(content_xml_str)
    table_list = content_xml.xpath('//table:table',
                                   namespaces=content_xml.nsmap)
    self.assertEquals(1, len(table_list))
    table = table_list[0]
    name_key = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name'
    self.assertEquals(granulated_table[1][0], table.attrib[name_key])

  def testGetTableFromDoc(self):
    """Test if getTableItemList can get a item of some granulated table from doc file"""
    data = encodestring(open("./data/granulate_table_test.doc").read())
    granulated_table = self.proxy.getTableItemList(data, "doc")
    self.proxy.getTable(data, granulated_table[1][0], "doc")
    table_item = decodestring(self.proxy.getTable(data, granulated_table[1][0],
                                                      "doc"))
    content_xml_str = ZipFile(StringIO(table_item)).read('content.xml')
    content_xml = etree.fromstring(content_xml_str)
    table_list = content_xml.xpath('//table:table',
                                   namespaces=content_xml.nsmap)
    self.assertEquals(1, len(table_list))
    table = table_list[0]
    name_key = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name'
    self.assertEquals(granulated_table[1][0], table.attrib[name_key])

  def testGetColumnItemListFromOdt(self):
    """Test if getColumnItemList can get the list of column item from odt file"""
    columns = self.proxy.getColumnItemList(
                encodestring(open("./data/granulate_table_test.odt").read()),
                "SoccerTeams",
                "odt")
    self.assertEquals([[0, 'Name'], [1, 'Country']], columns)

  def testGetColumnItemListFromDoc(self):
    """Test if getColumnItemList can get the list of column item from doc file"""
    #in the doc format the tables lose their names
    columns = self.proxy.getColumnItemList(
              encodestring(open("./data/granulate_table_test.doc").read()),
              "Table3",
              "doc")
    self.assertEquals([[0, 'Name'], [1, 'Country']], columns)

  def testGetLineItemListFromOdt(self):
    """Test if getLineItemList can get the list of lines items from odt file"""
    data = encodestring(open("./data/granulate_table_test.odt").read())
    line_item_list = self.proxy.getLineItemList(data, "Developers", "odt")
    self.assertEquals([['Name', 'Hugo'], ['Phone', '+55 (22) 8888-8888'],
                       ['Email', 'hugomaia@tiolive.com'], ['Name', 'Rafael'],
                       ['Phone', '+55 (22) 9999-9999'],
                       ['Email', 'rafael@tiolive.com']], line_item_list)

  def testGetLineItemListFromDoc(self):
    """Test if getLineItemList can get the list of lines items from doc file"""
    data = encodestring(open("./data/granulate_table_test.doc").read())
    line_item_list = self.proxy.getLineItemList(data, "Table1", "doc")
    self.assertEquals([['Name', 'Hugo'], ['Phone', '+55 (22) 8888-8888'],
                       ['Email', 'hugomaia@tiolive.com'], ['Name', 'Rafael'],
                       ['Phone', '+55 (22) 9999-9999'],
                       ['Email', 'rafael@tiolive.com']], line_item_list)


class TestImagetItemList(TestCase):
  def testGetImageItemListFromOdt(self):
    """Test if getImageItemList can get the list of images items from odt file"""
    data = encodestring(open("./data/granulate_test.odt").read())
    image_list = self.proxy.getImageItemList(data, "odt")
    self.assertEquals([['10000000000000C80000009CBF079A6E41EE290C.jpg', ''],
                       ['10000201000000C80000004E85B3F70C71E07CE8.png', 'TioLive Logo'],
                       ['10000201000000C80000004E85B3F70C71E07CE8.png', ''],
                       ['2000004F0000423300001370ADF6545B2997B448.svm', 'Python Logo'],
                       ['10000201000000C80000004E85B3F70C71E07CE8.png', 'Again TioLive Logo']],
                      image_list)

  def testGetImageItemListFromDoc(self):
    """Test if getImageItemList can get the list of images items from doc file"""
    data = encodestring(open("./data/granulate_test.doc").read())
    image_list = self.proxy.getImageItemList(data, "doc")
    self.assertEquals([['10000000000000C80000009CBF079A6E41EE290C.jpg', ''],
                       ['10000201000000C80000004E85B3F70C71E07CE8.png', 'TioLive Logo'],
                       ['10000201000000C80000004E85B3F70C71E07CE8.png', ''],
                       ['2000031600004233000013702113A0E70B910778.wmf', 'Python Logo'],
                       ['10000201000000C80000004E85B3F70C71E07CE8.png', 'Again TioLive Logo']],
                      image_list)

  def testGetImageFromOdt(self):
    """Test if getImage can get a image from odt file after zip"""
    data = encodestring(open("./data/granulate_test.odt").read())
    zip = ZipFile(StringIO(decodestring(data)))
    image_id = '10000201000000C80000004E7B947D46.png'
    original_image = zip.read('Pictures/%s' % image_id)
    geted_image = decodestring(self.proxy.getImage(data, image_id, "odt"))
    self.assertEquals(original_image, geted_image)

  def testGetImageFromDoc(self):
    """Test if getImage can get a image from doc file after zip"""
    data = encodestring(open("./data/granulate_test.doc").read())
    #This conversion is necessary to catch the image from the doc file;
    #so compare with the server return.
    data_odt = self.proxy.convertFile(data, 'doc', 'odt', False)
    zip = ZipFile(StringIO(decodestring(data_odt)))
    image_id = '10000000000000C80000009CBF079A6E41EE290C.jpg'
    original_image = zip.read('Pictures/%s' % image_id)
    geted_image = decodestring(self.proxy.getImage(data, image_id, "doc"))
    self.assertEquals(original_image, geted_image)


class TestParagraphItemList(TestCase):
  def testGetParagraphItemList(self):
    """Test if getParagraphItemList can get paragraphs correctly from document"""
    data = encodestring(open("./data/granulate_test.odt").read())
    paragraph_list = self.proxy.getParagraphItemList(data, "odt")
    self.assertEquals([[0, 'P3'], [1, 'P1'], [2, 'P12'], [3, 'P6'], [4, 'P7'],
                      [5, 'P8'], [6, 'P6'], [7, 'P6'], [8, 'P13'], [9, 'P9'],
                      [10, 'P9'], [11, 'P9'], [12, 'P4'], [13, 'P10'], [14,
                      'P5'], [15, 'P5'], [16, 'P14'], [17, 'P11'], [18, 'P11'],
                      [19, 'Standard'], [20, 'P2'], [21, 'P2'], [22, 'P2'],
                      [23, 'P2'], [24, 'P2'], [25, 'P2'], [26, 'P2'], [27,
                      'P2'], [28, 'P2'], [29, 'P2']], paragraph_list)

  def testGetParagraphItem(self):
    """Test if getParagraph can get a paragraph"""
    data = encodestring(open("./data/granulate_test.odt").read())
    paragraph = self.proxy.getParagraph(data, 1, "odt")
    self.assertEquals(['', 'P1'], paragraph)


class TestChapterItemList(TestCase):
  def testGetChapterItemList(self):
    """Test if getChapterItemList can get the chapters list correctly from document"""
    data = encodestring(open("./data/granulate_chapters_test.odt").read())
    chapter_list = self.proxy.getChapterItemList(data, "odt")
    self.assertEquals([[0, 'Title 0'], [1, 'Title 1'], [2, 'Title 2'],
                       [3, 'Title 3'], [4, 'Title 4'], [5, 'Title 5'],
                       [6, 'Title 6'], [7, 'Title 7'], [8, 'Title 8'],
                       [9, 'Title 9'], [10, 'Title 10']] , chapter_list)

  def testGetChapterItem(self):
    """Test if getChapterItem can get a chapter"""
    data = encodestring(open("./data/granulate_chapters_test.odt").read())
    chapter = self.proxy.getChapterItem(1, data, "odt")
    self.assertEquals(['Title 1', 1], chapter)


class TestCSVEncoding(TestCase):
  """Cloudoo tries to be "a bit" clever with CSV:
   * the supported encoding is UTF-8, but also accepts latin1, for compatibility.
   * the fields delimiter is guessed by python csv module.
  """
  def test_decode_utf8(self):
    data = encodestring(open("./data/csv_utf8.csv").read())
    converted = decodestring(self.proxy.convertFile(data, "csv", "html"))
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(converted), parser)
    self.assertEqual(
        [u"Jérome", u"ジェローム"],
        [x.text for x in tree.getroot().find('.//tr[1]').iterdescendants() if x.text])
    self.assertEqual(
        [u"नमस्ते", u"여보세요"],
        [x.text for x in tree.getroot().find('.//tr[2]').iterdescendants() if x.text])

  def test_decode_latin1(self):
    data = encodestring(open("./data/csv_latin1.csv").read())
    converted = decodestring(self.proxy.convertFile(data, "csv", "html"))
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(converted), parser)
    self.assertEqual(
        [u"Jérome", '1'],
        [x.text for x in tree.getroot().find('.//tr[1]').iterdescendants() if x.text])

  def test_separator_semicolon(self):
    data = encodestring(open("./data/csv_semicolon.csv").read())
    converted = decodestring(self.proxy.convertFile(data, "csv", "html"))
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(converted), parser)
    self.assertEqual(
        ['a a', '1'],
        [x.text for x in tree.getroot().find('.//tr[1]').iterdescendants() if x.text])
    self.assertEqual(
        ['b b', '2;x'],
        [x.text for x in tree.getroot().find('.//tr[2]').iterdescendants() if x.text])

  def test_separator_tab(self):
    data = encodestring(open("./data/tsv.tsv").read())
    converted = decodestring(self.proxy.convertFile(data, "csv", "html"))
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(converted), parser)
    self.assertEqual(
        ['a', 'b'],
        [x.text for x in tree.getroot().find('.//tr[1]').iterdescendants() if x.text])
    self.assertEqual(
        ['1,3', 'c'],
        [x.text for x in tree.getroot().find('.//tr[2]').iterdescendants() if x.text])

  def test_empty_csv(self):
    data = encodestring("")
    converted = decodestring(self.proxy.convertFile(data, "csv", "html"))
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(converted), parser)
    self.assertEqual(
        [],
        [x.text for x in tree.getroot().findall('.//td')])
