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

import unittest
from os.path import join, exists
from os import remove
from subprocess import Popen, PIPE
from xmlrpclib import ServerProxy, Fault
from base64 import encodestring, decodestring
from cloudoooTestCase import cloudoooTestCase, make_suite
from zipfile import ZipFile, is_zipfile
from types import DictType


class TestServer(cloudoooTestCase):
  """Test XmlRpc Server. Needs cloudooo server started"""
  
  def afterSetUp(self):
    """Creates a connection with cloudooo server"""
    self.proxy = ServerProxy("http://%s:%s/RPC2" % \
        (self.hostname, self.cloudooo_port), allow_none=True)

    self.text_expected_list = [['doc', 'Microsoft Word 6.0'], 
        ['doc', 'Microsoft Word 95'], 
        ['doc', 'Microsoft Word 97/2000/XP'], 
        ['htm', 'HTML Document (OpenOffice.org Writer)'], 
        ['html', 'HTML Document (OpenOffice.org Writer)'], 
        ['html', 'XHTML'], ['odt', 'ODF Text Document'], 
        ['ott', 'ODF Text Document Template'], 
        ['pdf', 'PDF - Portable Document Format'], 
        ['rtf', 'Rich Text Format'], ['sdw', 'StarWriter 3.0'], 
        ['sdw', 'StarWriter 4.0'], ['sdw', 'StarWriter 5.0'], 
        ['sxw', 'OpenOffice.org 1.0 Text Document'], 
        ['txt', 'Text'], ['txt', 'Text Encoded'],
        ['xhtml', 'XHTML'], ['pdb', 'AportisDoc (Palm)'],
        ['psw', 'Pocket Word']]
    
    self.text_expected_list.sort()
    
    self.presentation_expected_list = [['bmp', 'BMP - Windows Bitmap'], 
        ['emf', 'EMF - Enhanced Metafile'],
        ['eps', 'EPS - Encapsulated PostScript'],
        ['gif', 'GIF - Graphics Interchange Format'],
        ['htm', 'HTML Document (OpenOffice.org Impress)'],
        ['html', 'HTML Document (OpenOffice.org Impress)'],
        ['html', 'XHTML'], ['jfif', 'JPEG - Joint Photographic Experts Group'],
        ['jif', 'JPEG - Joint Photographic Experts Group'],
        ['jpe', 'JPEG - Joint Photographic Experts Group'],
        ['jpeg', 'JPEG - Joint Photographic Experts Group'],
        ['jpg', 'JPEG - Joint Photographic Experts Group'],
        ['met', 'MET - OS/2 Metafile'], ['odg', 'ODF Drawing (Impress)'],
        ['odp', 'ODF Presentation'],
        ['otp', 'ODF Presentation Template'],
        ['pbm', 'PBM - Portable Bitmap'], ['pct', 'PCT - Mac Pict'],
        ['pdf', 'PDF - Portable Document Format'], 
        ['pgm', 'PGM - Portable Graymap'], ['pict', 'PCT - Mac Pict'],
        ['png', 'PNG - Portable Network Graphic'],
        ['pot', 'Microsoft PowerPoint 97/2000/XP Template'],
        ['ppm', 'PPM - Portable Pixelmap'],
        ['pps', 'Microsoft PowerPoint 97/2000/XP'],
        ['ppt', 'Microsoft PowerPoint 97/2000/XP'],
        ['ras', 'RAS - Sun Raster Image'],
        ['sda', 'StarDraw 5.0 (OpenOffice.org Impress)'],
        ['sdd', 'StarDraw 3.0 (OpenOffice.org Impress)'],
        ['sdd', 'StarImpress 4.0'], ['sdd', 'StarImpress 5.0'],
        ['svg', 'SVG - Scalable Vector Graphics'], 
        ['svm', 'SVM - StarView Metafile'], 
        ['sxd', 'OpenOffice.org 1.0 Drawing (OpenOffice.org Impress)'],
        ['sxi', 'OpenOffice.org 1.0 Presentation'],
        ['tif', 'TIFF - Tagged Image File Format'],
        ['tiff', 'TIFF - Tagged Image File Format'],
        ['wmf', 'WMF - Windows Metafile'], 
        ['xhtml', 'XHTML'], ['xpm', 'XPM - X PixMap']]
    
    self.presentation_expected_list.sort()
  
  def _testConvertFile(self, input_url, output_url,
                      source_format, destination_format,
                      stdout_msg, zip=False):
    """Generic test to use convertFile"""
    data = encodestring(open(input_url).read())
    output_data = self.proxy.convertFile(data,
                                        source_format,
                                        destination_format, zip)
    open(output_url, 'w').write(decodestring(output_data))
    stdout, stderr = Popen("file -b %s" % output_url, shell=True,
         stdout=PIPE).communicate()
    self.assertEquals(stdout, stdout_msg)
    self.assertEquals(stderr, None)

  def testGetAllowedExtensionListByType(self):
    """Call getAllowedExtensionList and verify if the returns is a list with
    extension and ui_name. The request is by document type"""
    text_request = {'document_type': "text"}
    text_allowed_list = self.proxy.getAllowedExtensionList(text_request)
    text_allowed_list.sort()
    for arg in text_allowed_list:
      self.assertTrue(arg in self.text_expected_list, 
                    "%s not in %s" % (arg, self.text_expected_list))
    request_dict = {'document_type': "presentation"}
    presentation_allowed_list = self.proxy.getAllowedExtensionList(request_dict)
    presentation_allowed_list.sort()
    for arg in presentation_allowed_list:
      self.assertTrue(arg in self.presentation_expected_list, 
                    "%s not in %s" % (arg, self.presentation_expected_list))
  
  def testGetAllowedExtensionListByExtension(self):  
    """Call getAllowedExtensionList and verify if the returns is a list with
    extension and ui_name. The request is by extension"""
    doc_allowed_list = self.proxy.getAllowedExtensionList({'extension': "doc"})
    doc_allowed_list.sort()
    for arg in doc_allowed_list:
      self.assertTrue(arg in self.text_expected_list, 
                    "%s not in %s" % (arg, self.text_expected_list))

  def testGetAllowedExtensionListByMimetype(self):
    """Call getAllowedExtensionList and verify if the returns is a list with
    extension and ui_name. The request is by mimetype"""
    request_dict = {"mimetype": "application/msword"}
    msword_allowed_list = self.proxy.getAllowedExtensionList(request_dict)
    msword_allowed_list.sort()
    for arg in msword_allowed_list:
      self.assertTrue(arg in self.text_expected_list, 
                    "%s not in %s" % (arg, self.text_expected_list))

  def testConvertDocToOdt(self):
    """Test Convert Doc -> Odt"""
    self._testConvertFile("data/test.doc",
                          join(self.tmp_url, "document_output.odt"),
                          'doc',
                          'odt',
                          'OpenDocument Text\n')

  def testconvertDocToPdf(self):
    """Test Convert Doc -> Pdf"""
    self._testConvertFile("data/test.doc",
                          join(self.tmp_url, "document_output.pdf"),
                          'doc',
                          'pdf',
                          'PDF document, version 1.4\n')

  def testgetFileMetadataItemListWithoutData(self):
    """Test server using method getFileMetadataItemList. Without data
    converted""" 
    data = open(join('data','testMetadata.odt'),'r').read()
    metadata_dict = self.proxy.getFileMetadataItemList(encodestring(data),
                                                      'odt')
    self.assertEquals(metadata_dict.get("Data"), '')
    self.assertEquals(metadata_dict.get("Title"), "cloudooo Test")
    self.assertEquals(metadata_dict.get("Subject"), "Subject Test")
    self.assertEquals(metadata_dict.get("Description"), "cloudooo Comments")
    self.assertEquals(metadata_dict.get("Type"), "Text")
    self.assertEquals(metadata_dict.get("MIMEType"),\
        "application/vnd.oasis.opendocument.text")

  def testgetFileMetadataItemListWithData(self):
    """Test server using method getFileMetadataItemList. With data converted"""
    document_output_url = join(self.tmp_url, "testGetMetadata.odt")
    data = open(join('data','testMetadata.odt'),'r').read()
    metadata_dict = self.proxy.getFileMetadataItemList(encodestring(data),
                                                       "odt",
                                                       True)
    self.assertNotEquals(metadata_dict.get("Data"), None)
    open(document_output_url, 'w').write(decodestring(metadata_dict["Data"]))
    stdout, stderr = Popen("file -b %s" % document_output_url, shell=True,
        stdout=PIPE).communicate()
    self.assertEquals(stdout, 'OpenDocument Text\n')
    self.assertEquals(metadata_dict.get("Title"), "cloudooo Test")
    self.assertEquals(metadata_dict.get("Subject"), "Subject Test")
    self.assertEquals(metadata_dict.get("Description"), "cloudooo Comments")
    self.assertEquals(metadata_dict.get("Type"), "Text")
    self.assertEquals(metadata_dict.get("MIMEType"),\
        "application/vnd.oasis.opendocument.text")

  def testupdateFileMetadata(self):
    """Test server using method updateFileMetadata"""
    document_output_url = join(self.tmp_url, "testSetMetadata.odt")
    data = open(join('data','testMetadata.odt'),'r').read()
    odf_data = self.proxy.updateFileMetadata(encodestring(data), 'odt',
        {"Title":"testSetMetadata"})
    open(document_output_url, 'w').write(decodestring(odf_data))
    stdout, stderr = Popen("file -b %s" % document_output_url, shell=True,
        stdout=PIPE).communicate()
    self.assertEquals(stdout, 'OpenDocument Text\n')
    metadata_dict = self.proxy.getFileMetadataItemList(odf_data, 'odt')
    self.assertEquals(metadata_dict.get("Title"), "testSetMetadata")
    self.assertEquals(metadata_dict.get("CreationDate"), "9/7/2009 17:38:25")
    self.assertEquals(metadata_dict.get("Description"), "cloudooo Comments")

  def testupdateFileMetadataWithUserMetadata(self):
    """Test server using method updateFileMetadata with unsual metadata"""
    document_output_url = join(self.tmp_url, "testSetMetadata.odt")
    data = open(join('data','testMetadata.odt'),'r').read()

    odf_data = self.proxy.updateFileMetadata(encodestring(data),
                                              'odt',
                                              {"Reference":"testSetMetadata"})
    open(document_output_url, 'w').write(decodestring(odf_data))
    stdout, stderr = Popen("file -b %s" % document_output_url, shell=True,
        stdout=PIPE).communicate()
    self.assertEquals(stdout, 'OpenDocument Text\n')
    metadata_dict = self.proxy.getFileMetadataItemList(odf_data, 'odt')
    self.assertEquals(metadata_dict.get("Reference"), "testSetMetadata")

  def testupdateFileMetadataUpdateSomeMetadata(self):
    """Test server using method updateFileMetadata when the same metadata is
    updated"""
    document_output_url = join(self.tmp_url, "testSetMetadata.odt")
    data = open(join('data','testMetadata.odt'),'r').read()
    odf_data = self.proxy.updateFileMetadata(encodestring(data), 'odt',
                        {"Reference":"testSetMetadata", "Something":"ABC"})
    new_odf_data = self.proxy.updateFileMetadata(odf_data, 'odt',
                        {"Reference":"new value", "Something": "ABC"})
    open(document_output_url, 'w').write(decodestring(new_odf_data))
    stdout, stderr = Popen("file -b %s" % document_output_url, shell=True,
        stdout=PIPE).communicate()
    self.assertEquals(stdout, 'OpenDocument Text\n')
    metadata_dict = self.proxy.getFileMetadataItemList(new_odf_data, 'odt')
    self.assertEquals(metadata_dict.get("Reference"), "new value")
    self.assertEquals(metadata_dict.get("Something"), "ABC")

  def testupdateFileMetadataAlreadyHasMetadata(self):
    """Test document that already has metadata. Check if the metadata is not
    deleted"""
    data = open(join('data','testMetadata.odt'),'r').read()
    metadata_dict = self.proxy.getFileMetadataItemList(encodestring(data), 'odt')
    self.assertEquals(metadata_dict["Description"], "cloudooo Comments")
    self.assertEquals(metadata_dict["Keywords"], "Keywords Test")
    self.assertEquals(metadata_dict["Title"], "cloudooo Test")
    odf_data = self.proxy.updateFileMetadata(encodestring(data), 'odt',
        {"Title":"cloudooo Title"})
    odf_metadata_dict = self.proxy.getFileMetadataItemList(odf_data, 'odt')
    self.assertEquals(odf_metadata_dict["Description"], "cloudooo Comments")
    self.assertEquals(odf_metadata_dict["Keywords"], "Keywords Test")
    self.assertEquals(odf_metadata_dict["Title"], "cloudooo Title")

  def testWithZipFile(self):
    """Test if send a zipfile returns a document correctly"""
    output_msg = 'Zip archive data, at least v2.0 to extract\n'
    self._testConvertFile("data/test.zip",
                          join(self.tmp_url, "output_zipfile.zip"),
                          'html',
                          'txt',
                          output_msg,
                          True)

  def testSendZipAndReturnTxt(self):
    """Convert compressed html to txt"""
    output_url = join(self.tmp_url, "output.txt")
    self._testConvertFile("data/test.zip",
                          output_url,
                          'html',
                          'txt',
                          'ASCII text\n')

    self.assertEquals(open(output_url).read().endswith('cloudooo Test\n \n'), True)

  def testConvertPNGToSVG(self):
    """Test export png to svg"""
    self._testConvertFile("data/test.png",
                          join("output.svg"),
                          'png',
                          'svg',
                          'SVG Scalable Vector Graphics image\n')
  
  def testConvertPPTXToODP(self):
    """Test export pptx to odp"""
    self._testConvertFile("data/test.pptx",
                          join(self.tmp_url, "output.pptx"),
                          'pptx',
                          'odp',
                          'OpenDocument Presentation\n')

  def testConvertDocxToODT(self):
    """Test export docx to odt"""
    self._testConvertFile("data/test.docx",
                          join(self.tmp_url, "output_docx.odt"),
                          'docx',
                          'odt',
                          'OpenDocument Text\n')
  
  def testConvertPyToPDF(self):
    """Test export python to pdf"""
    self._testConvertFile("cloudoooTestCase.py",
                          join(self.tmp_url, "cloudoooTestCase.py"),
                          'py',
                          'pdf',
                          'PDF document, version 1.4\n')
 
  def testSendEmptyRequest(self):
    """Test to verify if the behavior of server is normal when a empty string
    is sent"""
    data = encodestring("")
    fail_msg = "This document can not be loaded, it is empty\n"
    try:
      self.proxy.convertFile(data, '', '')
      self.fail(fail_msg)
    except Fault, err:
      msg = "This format is not supported or is invalid"
      self.assertEquals(err.faultString.endswith(msg), True,
                        "ConvertFile\n" + err.faultString)
    
    res = self.proxy.getFileMetadataItemList(data, '')
    self.assertEquals(res['MIMEType'], "text/plain")
    res = decodestring(self.proxy.updateFileMetadata(data, '', 
                                         {"Subject": "subject"}))
    self.assertEquals(decodestring(res), '')

  def testConvertDocumentToInvalidFormat(self):
    """Try convert one document for a invalid format"""
    data = open(join('data','test.doc'),'r').read()
    error_msg = "This format is not supported or is invalid"
    try:
      self.proxy.convertFile(encodestring(data), 'doc', 'xyz')
      self.fail("")
    except Fault, err:
      err_str = err.faultString
      self.assertEquals(err_str.endswith(error_msg), True,
                        "%s\n%s" % (error_msg, err_str))
  
  def testConvertDocumentToImpossibleFormat(self):
    """Try convert one document to format not possible"""
    data = open(join('data','test.odp'),'r').read()
    error_msg = "This Document can not be converted for this format\n"
    try:
      self.proxy.convertFile(encodestring(data), 'odp', 'doc')
      self.fail("")
    except Fault, err:
      err_str = err.faultString
      self.assertEquals(err_str.endswith(error_msg), True,
                        "%s\n%s" % (error_msg, err_str))

  def testRunConvertMethod(self):
    """Test run_convert method"""
    data = open(join('data','test.doc'),'r').read()
    response_code, response_dict, response_message = \
              self.proxy.run_convert('test.doc', encodestring(data))
    self.assertEquals(response_code, 200)
    self.assertEquals(type(response_dict), DictType)
    self.assertNotEquals(response_dict['data'], '')
    self.assertEquals(sorted(response_dict.keys()),
                              ['data', 'meta', 'mime'])
    self.assertEquals(response_message, '')
    self.assertEquals(response_dict['meta']['MIMEType'],
                              'application/vnd.oasis.opendocument.text')

  def testRunConvertFailResponse(self):
    """Test run_convert method with invalid file"""
    data = open(join('data', 'test.doc'),'r').read()[:30]
    response_code, response_dict, response_message = \
              self.proxy.run_convert('test.doc', encodestring(data))
    self.assertEquals(response_code, 402)
    self.assertEquals(type(response_dict), DictType)
    self.assertEquals(response_dict, {})
    self.assertEquals(response_message.startswith('Traceback'), True)

  def testRunGenerateMethod(self):
    """Test run_generate method"""
    data = open(join('data', 'test.odt'),'r').read()
    generate_result = self.proxy.run_generate('test.odt',
                                      encodestring(data),
                                      None, 'pdf', 'odt')
    response_code, response_dict, response_message = generate_result
    self.assertEquals(response_code, 200)
    self.assertEquals(type(response_dict), DictType)
    self.assertNotEquals(response_dict['data'], '')
    self.assertEquals(response_dict['mime'], 'application/pdf')

  def testRunGenerateMethodConvertOdsToHTML(self):
    """Test run_generate method. This test is to validate a bug convertions to
    html"""
    data = open(join('data', 'test.ods'),'r').read()
    generate_result = self.proxy.run_generate('test.ods',
                                      encodestring(data),
                                      None, 'html', 'ods')
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

  def testPNGFileToConvertOdpToHTML(self):
    """Test run_generate method. This test if returns good png files"""
    data = open(join('data', 'test_png.odp'),'r').read()
    generate_result = self.proxy.run_generate('test_png.odp',
                                      encodestring(data),
                                      None, 'html', 'presentation')
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
      stdout, stderr = Popen("file -b %s" % png_path, shell=True,
         stdout=PIPE).communicate()
      self.assertEquals(stdout.startswith('PNG image data'), True, stdout)
      self.assertTrue("8-bit/color RGB" in stdout, stdout)
    finally:
      zipfile.close()
    if exists(output_url):
      remove(output_url)

  def testRunGenerateMethodConvertOdpToHTML(self):
    """Test run_generate method. This test is to validate a bug convertions to
    html"""
    data = open(join('data','test.odp'),'r').read()
    generate_result = self.proxy.run_generate('test.odp',
                                      encodestring(data),
                                      None, 'html', 'odp')
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

  def testRunGenerateMethodFailResponse(self):
    """Test run_generate method with invalid document"""
    data = open(join('data','test.odt'), 'r').read()[:100]
    generate_result = self.proxy.run_generate('test.odt',
                                      encodestring(data),
                                      None, 'odt', 'pdf')
    response_code, response_dict, response_message = generate_result
    self.assertEquals(response_code, 402)
    self.assertEquals(type(response_dict), DictType)
    self.assertEquals(response_dict, {})
    self.assertEquals(response_message.startswith('Traceback'), True)

  def testRunSetMetadata(self):
    """Test run_setmetadata method"""
    data = open(join('data','testMetadata.odt'),'r').read()
    setmetadata_result = self.proxy.run_setmetadata('testMetadata.odt', 
                          encodestring(data),
                          {"Title":"testSetMetadata", "Description": "Music"})
    response_code, response_dict, response_message = setmetadata_result
    self.assertEquals(response_code, 200)
    self.assertNotEquals(response_dict['data'], '')
    getmetadata_result = self.proxy.run_getmetadata('testMetadata.odt', 
                                                  response_dict['data'])
    response_code, response_dict, response_message = getmetadata_result
    self.assertEquals(response_code, 200)
    self.assertEquals(response_dict['meta']['MIMEType'], 
                      'application/vnd.oasis.opendocument.text') 
    self.assertEquals(response_dict['meta']['Description'], "Music")
    setmetadata_result = self.proxy.run_setmetadata('testMetadata.odt', 
                          encodestring(data),
                          {"Title":"Namie's working record", 
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
    data = open(join('data','testMetadata.odt'),'r').read()[:100]
    setmetadata_result = self.proxy.run_setmetadata('testMetadata.odt', 
                          encodestring(data),
                          {"Title":"testSetMetadata", "Description": "Music"})
    response_code, response_dict, response_message = setmetadata_result
    self.assertEquals(response_code, 402)
    self.assertEquals(response_dict, {})
    self.assertEquals(response_message.startswith('Traceback'), True)

  def testGetAllowedTargetItemList(self):
    """Test if filter name returns correctly with ERP5 API"""
    mimetype = 'application/vnd.oasis.opendocument.text'
    response_code, response_dict, response_message = \
                  self.proxy.getAllowedTargetItemList(mimetype)
    self.assertEquals(response_code, 200)
    self.assertEquals(len(response_dict['response_data']), 31)
    self.assertTrue(['htm', 'HTML Document'] in response_dict['response_data'])


def test_suite():
  return make_suite(TestServer)
  
if __name__ == "__main__":
  import sys
  from cloudoooTestCase import loadConfig
  loadConfig(sys.argv[1])
  suite = unittest.TestLoader().loadTestsFromTestCase(TestServer)
  unittest.TextTestRunner(verbosity=2).run(suite)
