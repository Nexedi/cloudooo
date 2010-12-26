#!/usr/bin/env python

import unittest
import sys
from base64 import encodestring
from xmlrpclib import ServerProxy
from getopt import getopt, GetoptError

DOCUMENT_STRING = """MemoryMonitor - TimeoutMonitor -
RequestMonitor\n\nOOHandler\n\nMimemapper\n\nERP5\n"""
HOSTNAME = PORT = None


class CloudoooTestCase(unittest.TestCase):
  """ """

  def setUp(self):
    self.proxy_address = "http://%s:%s" % (HOSTNAME, PORT)

  def test_run_generate(self):
    data = encodestring(DOCUMENT_STRING)
    proxy = ServerProxy(self.proxy_address, allow_none=True)
    res = proxy.run_generate("t.text", data, None, 'pdf', 'text/plain')
    self.assertEquals(res[1]['mime'], "application/pdf")
    self.assertEquals(res[0], 200)

  def test_set_metadata(self):
    data = encodestring(DOCUMENT_STRING)
    proxy = ServerProxy(self.proxy_address, allow_none=True)
    odt_data = proxy.convertFile(data, 'txt', 'odt')
    metadata_dict = proxy.getFileMetadataItemList(odt_data, 'odt')
    self.assertEquals(metadata_dict["MIMEType"],
                          'application/vnd.oasis.opendocument.text')
    res = proxy.run_setmetadata("t.odt", odt_data, {"Title": "test"})
    self.assertEquals(res[0], 200)
    response_code, response_dict, response_message = \
                    proxy.run_convert("t.odt", res[1]['data'])
    self.assertEquals(response_code, 200)
    self.assertEquals(response_dict['meta']['Title'], "test")


def main():
  global PORT, HOSTNAME
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "",
                                ["port=", "hostname="])
  except GetoptError, e:
    print >> sys.stderr, "%s \nUse --port and --hostname" % e
    sys.exit(2)

  for opt, arg in opt_list:
    if opt == "--port":
      PORT = arg
    elif opt == "--hostname":
      HOSTNAME = arg

  if not HOSTNAME and not PORT:
    print >> sys.stderr, "Use --port and --hostname"
    sys.exit(2)
  suite = unittest.TestLoader().loadTestsFromTestCase(CloudoooTestCase)
  unittest.TextTestRunner(verbosity=2).run(suite)
