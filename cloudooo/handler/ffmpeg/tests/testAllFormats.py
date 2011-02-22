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

import unittest
import magic
import re
from cloudooo.handler.ffmpeg.handler import FFMPEGHandler
from cloudooo.handler.tests.handlerTestCase import HandlerTestCase, make_suite


file_detector = magic.Magic()

class TestAllFormats(HandlerTestCase):

  def afterSetUp(self):
    self.data = open("./data/test.ogv").read()
    self.input = FFMPEGHandler(self.tmp_url, self.data, "ogv")
  
  def testAviFormat(self):
    """Test convert file to avi format"""
    output_data = self.input.convert("avi")
    file_format = file_detector.from_buffer(output_data)
    self.assertEqual(file_format, ('RIFF (little-endian) data, AVI, 640 x 352,'
                                    +' >30 fps, video: FFMpeg MPEG-4, '
                                    +'audio: MPEG-1 Layer 1 or 2 (mono, '
                                    +'48000 Hz)'))
  
  def testMp4Format(self):
    """Test convert file to mp4 format"""
    output_data = self.input.convert("mp4")
    file_format = file_detector.from_buffer(output_data)
    self.assertEqual(file_format, 'ISO Media, MPEG v4 system, version 2')

  def testWebMFormat(self):
    """Test convert file to WebM format"""
    output_data = self.input.convert("webm")
    # XXX This might use magic, but it was not able to find witch format
    # this format belongs to
    file_format = re.findall("webm", output_data)
    self.assertEqual(file_format, ['webm'])

  def testFlvFormat(self):
    """Test convert file to flash format"""
    output_data = self.input.convert("flv")
    file_format = file_detector.from_buffer(output_data)
    self.assertEqual(file_format, 'Macromedia Flash Video')

  def testMpegFormat(self):
    """Test convert file to Mpeg format"""
    output_data = self.input.convert("mpeg")
    file_format = file_detector.from_buffer(output_data)
    self.assertEqual(file_format, 'MPEG sequence, v1, system multiplex')

  def testMkvFormat(self):
    """Test convert file to matroska format"""
    output_data = self.input.convert("mkv")
    # XXX This might use magic, but it was not able to find witch format
    # this format belongs to
    file_format = re.findall("matroska", output_data)
    self.assertEqual(file_format, ['matroska'])

  def testOggFormat(self):
    """Test convert file to ogg format"""
    output_data = self.input.convert("ogg")
    file_format = file_detector.from_buffer(output_data)
    self.assertEqual(file_format, 'Ogg data, Theora video')


def test_suite():
  return make_suite(TestAllFormats)
