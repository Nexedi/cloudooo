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

from xmlrpclib import ServerProxy
from base64 import encodestring, decodestring
from multiprocessing import Process, Array
from cloudoooTestCase import CloudoooTestCase, make_suite
import magic

DAEMON = True
mime_decoder = magic.Magic(mime=True)

def basicTestToGenerate(id, proxy, data, source_format, destination_format,
                        result_list):
  """Test to use method generate of server"""
  document = proxy.convertFile(data, source_format, destination_format)
  mimetype = mime_decoder.from_buffer(decodestring(document))
  assert mimetype == 'application/pdf'
  result_list[id] = True

class TestHighLoad(CloudoooTestCase):
  """Test with many simultaneous connection"""

  def afterSetUp(self):
    """Creates connection with cloudooo Server"""
    self.proxy = ServerProxy("http://%s:%s" % (self.hostname, self.cloudooo_port))

  def testGenerateHighLoad(self):
    """Sends many request to Server. Calling generate method"""
    process_list = []
    data = encodestring(open("data/test.doc", 'r').read())
    LOOP = 50
    result_list = Array('i', [False]*LOOP)
    for id in range(LOOP):
      process = Process(target=basicTestToGenerate, args=(id, self.proxy, data,
                                                          'doc', 'pdf',
                                                          result_list))
      process.start()
      process_list.append(process)

    for proc in process_list[:]:
      proc.join()
      del proc
    self.assertTrue(all(result_list))


def test_suite():
  return make_suite(TestHighLoad)

