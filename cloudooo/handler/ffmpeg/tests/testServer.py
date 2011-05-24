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

from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite
from xmlrpclib import ServerProxy
from os.path import join
from base64 import encodestring, decodestring
from magic import Magic

DAEMON = True


class TestServer(HandlerTestCase):
  """Test XmlRpc Server. Needs cloudooo server started"""

  def afterSetUp(self):
    """Creates a connection with cloudooo server"""
    self.proxy = ServerProxy("http://%s:%s/RPC2" % \
        (self.hostname, self.cloudooo_port), allow_none=True)
    self.data = open(join('data', 'test.ogv'), 'r').read()

  def testConvertVideo(self):
    """Converts ogv video to mpeg format"""
    video = self.proxy.convertFile(encodestring(self.data),
                                      "ogv",
                                      "mpeg")
    mime = Magic(mime=True)
    mimetype = mime.from_buffer(decodestring(video))
    self.assertEquals(mimetype, 'video/mpeg')

  def testGetMetadata(self):
    """test if metadata are extracted correctly"""
    metadata = self.proxy.getFileMetadataItemList(encodestring(self.data), "ogv")
    self.assertEquals(metadata["Encoder"], 'Lavf52.64.2')

  def testSetMetadata(self):
    """Test if metadata is inserted correctly"""
    new_data = self.proxy.updateFileMetadata(encodestring(self.data),
                                          "ogv",
                                          {"title": "Server Set Metadata Test"})
    metadata = self.proxy.getFileMetadataItemList(new_data, "ogv")
    self.assertEquals(metadata["Encoder"], 'Lavf52.64.2')
    self.assertEquals(metadata["Title"], 'Server Set Metadata Test')


def test_suite():
  return make_suite(TestServer)
