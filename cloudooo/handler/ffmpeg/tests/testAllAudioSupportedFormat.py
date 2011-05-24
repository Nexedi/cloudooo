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
from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite

DAEMON = True

class TestAllSupportedFormat(HandlerTestCase):

  def afterSetUp(self):
    self.file_detector = Magic(mime=True)
    self.proxy = ServerProxy("http://%s:%s/RPC2" % \
        (self.hostname, self.cloudooo_port), allow_none=True)

  def testMP3Format(self):
    """Test convert file to mp3 format the reverse convertion"""
    mp3_mimetype, ogg_mimetype = self.runTestForType("mp3")
    # XXX This might expect 'audio/mpeg' but magic only got
    # 'application/octet-stream'
    self.assertEquals(mp3_mimetype, 'application/octet-stream')
    # XXX This might expect 'audio/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogg_mimetype, 'application/ogg')

  def testWAVFormat(self):
    """Test convert file to wav format the reverse convertion"""
    wav_mimetype, ogg_mimetype = self.runTestForType("wav")
    # XXX this might expect 'audio/vnd.wave' but magic only got 'audio/x-wav'
    self.assertEquals(wav_mimetype, 'audio/x-wav')
    # XXX This might expect 'audio/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogg_mimetype, 'application/ogg')

  def testMIDFormat(self):
    """Test convert file to mid format and the reverse convertion"""
    mid_mimetype, ogg_mimetype = self.runTestForType("mid")
    self.assertEquals(mid_mimetype, 'audio/rtp-midi')
    # XXX This might expect 'audio/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogg_mimetype, 'application/ogg')

  def runTestForType(self, destination_format):
    """Converts audio files from ogg to destination_format and then to
    ogg again"""
    data = open(join('data', 'test.ogg'), 'r').read()
    converted_data = self.proxy.convertFile(encodestring(data),
                                      "ogg",
                                      destination_format)
    destination_mimetype = self.file_detector.from_buffer(decodestring(
                                                          converted_data))
    ogg_data = self.proxy.convertFile(converted_data,
                                      destination_format,
                                      "ogg")
    ogg_mimetype = self.file_detector.from_buffer(decodestring(ogg_data))
    return (destination_mimetype, ogg_mimetype)


def test_suite():
  return make_suite(TestAllSupportedFormat)
