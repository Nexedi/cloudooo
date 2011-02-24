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
from cloudooo.handler.ffmpeg.handler import FFMPEGHandler
from cloudooo.handler.tests.handlerTestCase import HandlerTestCase, make_suite


class TestFFMPEGHandler(HandlerTestCase):

  def afterSetUp(self):
    self.data = open("./data/test.ogv").read()
    self.input = FFMPEGHandler(self.tmp_url, self.data, "ogv")

  def testConvertVideo(self):
    """Test coversion of video to another format"""
    file_detector = magic.Magic()
    output_data = self.input.convert("ogg")
    file_format = file_detector.from_buffer(output_data)
    self.assertEqual(file_format, 'Ogg data, Theora video')
  
  def testgetMetadata(self):
    """Test if metadata is extracted from"""
    self.assertRaises(NotImplementedError, self.input.getMetadata)
  
  def testsetMetadata(self):
    """ Test if metadata are inserted correclty """
    self.assertRaises(NotImplementedError, self.input.setMetadata)


def test_suite():
  return make_suite(TestFFMPEGHandler)