import unittest
import sys
from os import environ
from ConfigParser import ConfigParser
from xmlrpclib import ServerProxy
from magic import Magic
from base64 import encodestring, decodestring

config = ConfigParser()

def make_suite(test_case):
  """Function is used to run all tests together"""
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(test_case))
  return suite


class TestCase(unittest.TestCase):

  def setUp(self):
    server_cloudooo_conf = environ.get("server_cloudooo_conf", None)
    if server_cloudooo_conf is not None:
      config.read(server_cloudooo_conf)
    self.hostname = config.get("server:main", "host")
    self.port = config.get("server:main", "port")
    self.env_path = config.get("app:main", "env-path")
    self.proxy = ServerProxy(("http://%s:%s/RPC2" % (self.hostname, self.port)),\
                allow_none=True)

  def _getFileType(self, output_data):
    mime = Magic(mime=True)
    mimetype = mime.from_buffer(decodestring(output_data))
    return mimetype

  def _testConvertFile(self, input_url, source_format, destination_format,
                      destination_mimetype, zip=False):
    """ Generic test for converting file """
    output_data = self.proxy.convertFile(encodestring(open(input_url).read()),
                                                      source_format,
                                                      destination_format,
                                                      zip)
    file_type = self._getFileType(output_data)
    self.assertEquals(file_type, destination_mimetype)

  def _testGetMetadata(self, input_url, source_format, expected_metadata):
    """ Generic tes for getting metadata file"""
    metadata_dict = self.proxy.getFileMetadataItemList(
                            encodestring(open(input_url).read()),
                            source_format)
    self.assertEquals(expected_metadata, metadata_dict)

  def _testUpdateMetadata(self, input_url, source_format, metadata_dict, 
                          expected_metadata):
    """ Generic test for setting metadata for file """
    output_data = self.proxy.updateFileMetadata(encodestring(open(input_url).read()),
                                            source_format,
                                            metadata_dict)
    new_metadata_dict = self.proxy.getFileMetadataItemList(
                            encodestring(output_data),
                            source_format)
    self.assertEquals(new_metadata_dict, expected_metadata)

  def ConversionScenarioList(self):
    """This method must be overwrited into subclasses"""
    return []

  def runConversionList(self, scenarios):
    for scenario in scenarios:
      self._testConvertFile(*scenario)

  def GetMetadataScenarioList(self):
    """This method must be overwrited into subclasses"""
    return []

  def runGetMetadataList(self, scenarios):
    for scenario in scenarios:
      self._testGetMetadata(*scenario)

  def UpdateMetadataScenarioList(self):
    """This method must be overwrited into subclasses"""
    return []

  def runUpdateMetadataList(self, scenarios):
    for scenario in scenarios:
      self._testUpdateMetadata(*scenario)

