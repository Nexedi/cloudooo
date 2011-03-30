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
from cloudooo.handler.ffmpeg.handler import Handler
from cloudooo.handler.tests.handlerTestCase import HandlerTestCase, make_suite


class TestAllSupportedFormat(HandlerTestCase):

  def afterSetUp(self):
    self.data = open("./data/test.ogv").read()
    self.kw = dict(env=dict(PATH=self.env_path))
    self.input = Handler(self.tmp_url, self.data, "ogv", **self.kw)
    self.file_detector = Magic(mime=True)

  def afterFormat(self, data, source_format):
    ogv_file = Handler(self.tmp_url, data, source_format, **self.kw)
    ogv_data = ogv_file.convert("ogv")
    ogv_mimetype = self.file_detector.from_buffer(ogv_data)
    return ogv_mimetype

  def testAviFormat(self):
    """Test convert file to avi format the reverse convertion"""
    avi_data = self.input.convert("avi")
    avi_mimetype = self.file_detector.from_buffer(avi_data)
    # XXX this might expect 'video/avi' but magic only got 'video/x-msvideo'
    self.assertEquals(avi_mimetype, 'video/x-msvideo')
    ogv_mimetype = self.afterFormat(avi_data,"avi")
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def testMp4Format(self):
    """Test convert file to mp4 format the reverse convertion"""
    mp4_data = self.input.convert("mp4")
    mp4_mimetype = self.file_detector.from_buffer(mp4_data)
    self.assertEquals(mp4_mimetype, 'video/mp4')
    ogv_mimetype = self.afterFormat(mp4_data,"mp4")
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def testWebMFormat(self):
    """Test convert file to WebM format and the reverse convertion"""
    webm_data = self.input.convert("webm")
    webm_mimetype = self.file_detector.from_buffer(webm_data)
    self.assertEquals(webm_mimetype, 'video/webm')
    ogv_mimetype = self.afterFormat(webm_data,"webm")
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def testFlvFormat(self):
    """Test convert file to flash format the reverse convertion"""
    flv_data = self.input.convert("flv")
    flv_mimetype = self.file_detector.from_buffer(flv_data)
    # XXX this might expect 'application/x-shockwave-flash' but magic only got
    # 'video/x-flv'
    self.assertEquals(flv_mimetype, 'video/x-flv')
    ogv_mimetype = self.afterFormat(flv_data,"flv")
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def testMpegFormat(self):
    """Test convert file to Mpeg format the reverse convertion"""
    mpeg_data = self.input.convert("mpeg")
    mpeg_mimetype = self.file_detector.from_buffer(mpeg_data)
    self.assertEquals(mpeg_mimetype, 'video/mpeg')
    ogv_mimetype = self.afterFormat(mpeg_data,"mpeg")
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

  def testMkvFormat(self):
    """Test convert file to matroska format the reverse convertion"""
    mkv_data = self.input.convert("mkv")
    mkv_mimetype = self.file_detector.from_buffer(mkv_data)
    # XXX This might expect 'video/x-matroska' but magic only got
    # 'application/octet-stream'
    self.assertEquals(mkv_mimetype, 'application/octet-stream')
    ogv_mimetype = self.afterFormat(mkv_data,"mkv")
    # XXX This might expect 'video/ogg' but magic only got 'application/ogg'
    self.assertEquals(ogv_mimetype, 'application/ogg')

def test_suite():
  return make_suite(TestAllSupportedFormat)
