import unittest
from xmlrpclib import ServerProxy
from magic import Magic


class TestCase(unittest.TestCase):

  def getConnection(self):
    proxy_address = "http://%s:%s" % (HOSTNAME, PORT)
    proxy = ServerProxy(proxy_address, allow_none=True)
    return proxy

  def _getFileType(self, output_data):
    mime = Magic(mime=True)
    mimetype = mime.from_buffer(decodestring(output_data))

  def _testConvertFile(self, input_url, source_format, destination_format,
                      destination_mimetype):
    """ Generic test for converting file """
    output_data = proxy.convertFile(encodestring(open(input_url).read()),
                                                      source_format,
                                                      destination_format)
    file_type = self._getFileType(output_data)
    self.assertEquals(mimetype, destination_mimetype)

  def _testGetMetadata(self, input_url, source_format, key, value):
    """ Generic tes for getting metadata file"""
    metadata_dict = proxy.getFileMetadataItemList(
                            encodestring(open(input_url).read()),
                            source_format)
    self.assertEquals(metadata_dict[key], value)

  def _testUpdateMetadata(self, input_url, source_format, metadata_dict):
    """ Generic test for setting metadata for file """
    output_data = proxy.updateFileMetadata(encodestring(open(input_url).read()),
                                            source_format,
                                            metadata_dict)
    new_metadata_dict = proxy.getFileMetadataItemList(
                            encodestring(output_data),
                            source_format)

  def getConversionScenarioList(self):
    """This method must be overwrited into subclasses"""
    return []

  def getConversionList(self):
    for scenario in self.getConversionScenarioList():
      self._testConvertFile(*scenario)

  def getGetMetadataScenarioList(self):
    """This method must be overwrited into subclasses"""
    return []

  def getGetMetadataList(self):
    for scenario in self.getGetMetadataScenarioList():
      self._testGetMetadata(*scenario)

  def getUpdateMetadataScenarioList(self):
    """This method must be overwrited into subclasses"""
    return []

  def getUpdateMetadataList(self):
    for scenario in self.getUpdateMetadataScenarioList():
      self._testUpdateMetadata(*scenario)

