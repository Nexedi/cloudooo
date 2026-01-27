##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Priscila Manhaes  <psilva@iff.edu.br>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################

import unittest
from os import environ, path
from configparser import ConfigParser
from xmlrpc.client import ServerProxy, Fault
from magic import Magic
from base64 import encodebytes, decodebytes

config = ConfigParser()

def make_suite(test_case):
  """Function is used to run all tests together"""
  suite = unittest.TestSuite()
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test_case))
  return suite


class TestCase(unittest.TestCase):

  def setUp(self):
    server_cloudooo_conf = environ.get("server_cloudooo_conf", None)
    if server_cloudooo_conf is not None:
      config.read(server_cloudooo_conf)
    self.hostname = config.get("server:main", "host")
    self.port = config.get("server:main", "port")
    self.env_path = config.get("app:main", "env-path")
    #create temporary path for some files
    self.working_path = config.get("app:main", "working_path")
    self.tmp_url = path.join(self.working_path, "tmp")
    self.proxy = ServerProxy(("http://{}:{}/RPC2".format(self.hostname, self.port)),\
                allow_none=True)
    self.addCleanup(self.proxy('close'))
    self.afterSetUp()

  def afterSetUp(self):
    """Must be overwrite into subclass in case of need """

  def _getFileType(self, output_data:str) -> str:
    """get file type of `output_data`
    output_data is base64
    """
    mime = Magic(mime=True)
    mimetype = mime.from_buffer(decodebytes(output_data.encode()))
    return mimetype

  def _testConvertFile(self, input_url, source_format, destination_format,
                      destination_mimetype, zip=False, refresh=False, conversion_kw=None):
    """ Generic test for converting file """
    fault_list = []
    try:
      with open(input_url, 'rb') as f:
        data = f.read()
      output_data = self.proxy.convertFile(
        encodebytes(data).decode(),
        source_format,
        destination_format,
        zip,
        refresh,
        conversion_kw or {},
      )
      file_type = self._getFileType(output_data)
      if destination_mimetype != None:
        self.assertEqual(file_type, destination_mimetype)
      else:
        if file_type.endswith(": empty"):
          fault_list.append((source_format, destination_format, file_type))
    except Fault as err:
      fault_list.append((source_format, destination_format, err.faultString))
    if fault_list:
      template_message = 'input_format: %r\noutput_format: %r\n traceback:\n%s'
      message = '\n'.join([template_message % fault for fault in fault_list])
      self.fail('Failed Conversions:\n' + message)

  def _testFaultConversion(self, data:bytes, source_format:str, destination_format:str):
    """ Generic test for fail converting"""
    self.assertRaises(Fault, self.proxy.convertFile, (data,
                                                      source_format,
                                                      destination_format))

  def _testGetMetadata(self, input_url:str, source_format:str, expected_metadata:dict,
                      base_document=False):
    """ Generic tes for getting metadata file"""
    with open(input_url, 'rb') as f:
      input_data = f.read()
    metadata_dict = self.proxy.getFileMetadataItemList(
                            encodebytes(input_data).decode(),
                            source_format,
                            base_document)
    for key,value in expected_metadata.items():
      self.assertEqual(metadata_dict[key], value)

  def _testFaultGetMetadata(self, data:bytes, source_format:str):
    """ Generic test for fail converting"""
    self.assertRaises(Fault, self.proxy.getFileMetadataItemList, (data,
                                                                  source_format))

  def _testUpdateMetadata(self, input_url:str, source_format:str, metadata_dict:dict):
    """ Generic test for setting metadata for file """
    with open(input_url, 'rb') as f:
      input_data = f.read()
    output_data = self.proxy.updateFileMetadata(encodebytes(input_data).decode(),
                                            source_format,
                                            metadata_dict)
    new_metadata_dict = self.proxy.getFileMetadataItemList(
                            output_data,
                            source_format,
                            False)
    for key, value in metadata_dict.items():
      self.assertEqual(new_metadata_dict[key], value)

  def _testRunConvert(self, filename:str, data:bytes, expected_response_code:int,
                      response_dict_data, response_dict_keys:list[str],
                      expected_response_message, response_dict_meta=None):
    """Generic test for run_convert"""
    response_code, response_dict, response_message = \
              self.proxy.run_convert(filename, encodebytes(data).decode())
    self.assertEqual(response_code, expected_response_code)
    self.assertIsInstance(response_dict, dict)
    if expected_response_code == 402:
      self.assertEqual(response_dict, {})
      self.assertTrue(response_message.endswith(expected_response_message),
                    "%s != %s" % (response_message, expected_response_message))
    else:
      self.assertNotEqual(response_dict['data'], response_dict_data)
      self.assertEqual(sorted(response_dict.keys()), response_dict_keys)
      self.assertEqual(response_message, expected_response_message)
      self.assertEqual(response_dict['meta']['MIMEType'], response_dict_meta)

  def ConversionScenarioList(self):
    """
    Method used to convert files
    must be overwrited into subclasses
    """
    return []

  def runConversionList(self, scenarios):
    for scenario in scenarios:
      with self.subTest(scenario):
        self._testConvertFile(*scenario)

  def GetMetadataScenarioList(self):
    """
    Method used to getMetadata from file
    must be overwrited into subclasses
    """
    return []

  def runGetMetadataList(self, scenarios):
    for scenario in scenarios:
      with self.subTest(scenario):
        self._testGetMetadata(*scenario)

  def UpdateMetadataScenarioList(self):
    """
    Method used to set/updateMetadata from file
    must be overwrited into subclasses
    """
    return []

  def runUpdateMetadataList(self, scenarios):
    for scenario in scenarios:
      with self.subTest(scenario):
        self._testUpdateMetadata(*scenario)

  def FaultConversionScenarioList(self):
    """
    Method used to verify fault conversion scenarios
    must be overwrited into subclasses
    """
    return []

  def runFaultConversionList(self, scenarios):
    for scenario in scenarios:
      with self.subTest(scenario):
        self._testFaultConversion(*scenario)

  def FaultGetMetadataScenarioList(self):
    """
    Method used to verify fault getMetadata scenarios
    must be overwrited into subclasses
    """
    return []

  def runFaultGetMetadataList(self, scenarios):
    for scenario in scenarios:
      with self.subTest(scenario):
        self._testFaultGetMetadata(*scenario)

  def ConvertScenarioList(self):
    """
    Method to verify run_convert
    must be overwrited into subclasses
    """
    return []

  def runConvertScenarioList(self, scenarios):
    for scenario in scenarios:
      with self.subTest(scenario):
        self._testRunConvert(*scenario)

