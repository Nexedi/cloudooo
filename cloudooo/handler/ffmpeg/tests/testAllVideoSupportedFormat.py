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

from magic import Magic
from xmlrpclib import ServerProxy
from os.path import join
from base64 import encodestring, decodestring
from cloudooo.handler.tests.handlerTestCase import HandlerTestCase, make_suite

DAEMON = True

class TestAllSupportedFormat(HandlerTestCase):
  """Test XmlRpc Server. Needs cloudooo server started"""

  def afterSetUp(self):
    self.file_detector = Magic(mime=True)
    self.proxy = ServerProxy("http://%s:%s/RPC2" % \
        (self.hostname, self.cloudooo_port), allow_none=True)

  def testAviFormat(self):
    """Test convert file to avi format the reverse convertion"""
    avi_mimetype, ogv_mimetype = self.runTestForType("avi")
    # XXX this might expect 'video/avi' but magic only got 'video/x-msvideo'
    self.assertEquals(avi_mimetype, 'video/x-msvideo')
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def testMp4Format(self):
    """Test convert file to mp4 format the reverse convertion"""
    mp4_mimetype, ogv_mimetype = self.runTestForType("mp4")
    self.assertEquals(mp4_mimetype, 'video/mp4')
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def testWebMFormat(self):
    """Test convert file to WebM format and the reverse convertion"""
    webm_mimetype, ogv_mimetype = self.runTestForType("webm")
    self.assertEquals(webm_mimetype, 'video/webm')
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def testFlvFormat(self):
    """Test convert file to flash format the reverse convertion"""
    flv_mimetype, ogv_mimetype = self.runTestForType("flv")
    # XXX this might expect 'application/x-shockwave-flash' but magic only got
    # 'video/x-flv'
    self.assertEquals(flv_mimetype, 'video/x-flv')
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def testMpegFormat(self):
    """Test convert file to Mpeg format the reverse convertion"""
    mpeg_mimetype, ogv_mimetype = self.runTestForType("mpeg")
    self.assertEquals(mpeg_mimetype, 'video/mpeg')
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def testMkvFormat(self):
    """Test convert file to matroska format the reverse convertion"""
    mkv_mimetype, ogv_mimetype = self.runTestForType("mkv")
    # XXX This might expect 'video/x-matroska' but magic only got
    # 'application/octet-stream'
    self.assertEquals(mkv_mimetype, 'application/octet-stream')
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def runTestForType(self, destination_format):
    """Converts video files from ogv to destination_format and then to
    ogv again"""
    data = open(join('data', 'test.ogv'), 'r').read()
    converted_data = self.proxy.convertFile(encodestring(data),
                                      "ogv",
                                      destination_format)
    destination_mimetype = self.file_detector.from_buffer(decodestring(
                                                          converted_data))
    ogv_data = self.proxy.convertFile(converted_data,
                                      destination_format,
                                      "ogv")
    ogv_mimetype = self.file_detector.from_buffer(decodestring(ogv_data))
    return (destination_mimetype, ogv_mimetype)

def test_suite():
  return make_suite(TestAllSupportedFormat)
