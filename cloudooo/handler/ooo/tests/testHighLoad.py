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
import os
import subprocess
from xmlrpclib import ServerProxy
from base64 import encodestring, decodestring
from multiprocessing import Process
from cloudoooTestCase import CloudoooTestCase, make_suite


class TestHighLoad(CloudoooTestCase):
  """Test with many simultaneous connection"""

  def afterSetUp(self):
    """Creates connection with cloudooo Server"""
    self.proxy = ServerProxy("http://%s:%s" % (self.hostname, self.cloudooo_port))

  def basicTestToGenerate(self, id, data, source_format, destination_format):
    """Test to use method generate of server"""
    document = self.proxy.convertFile(data, source_format, destination_format)
    document_output_url = os.path.join(self.tmp_url, "%s.%s" % (id, destination_format))
    open(document_output_url, 'wb').write(decodestring(document))
    stdout, stderr = subprocess.Popen("file -b %s" % document_output_url,
        shell=True, stdout=subprocess.PIPE).communicate()
    self.assertEquals(stdout, 'PDF document, version 1.4\n')
    self.assertEquals(stderr, None)
    os.remove(document_output_url)
    self.assertEquals(os.path.exists(document_output_url), False)

  def testGenerateHighLoad(self):
    """Sends many request to Server. Calling generate method"""
    process_list = []
    data = open("data/test.doc", 'r').read()
    for id in range(50):
      process = Process(target=self.basicTestToGenerate, args=(id,
        encodestring(data), 'doc', 'pdf'))
      process.start()
      process_list.append(process)

    for proc in process_list[:]:
      proc.join()
      del proc


def test_suite():
  return make_suite(TestHighLoad)

if __name__ == "__main__":
  import sys
  from cloudoooTestCase import loadConfig
  loadConfig(sys.argv[1])
  suite = unittest.TestLoader().loadTestsFromTestCase(TestHighLoad)
  unittest.TextTestRunner(verbosity=2).run(suite)
