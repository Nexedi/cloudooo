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
from cloudooo.tests.handlerTestCase import HandlerTestCase, make_suite


class TestHandler(HandlerTestCase):

  def afterSetUp(self):
    self.data = open("./data/test.ogv").read()
    self.kw = dict(env=dict(PATH=self.env_path))
    self.input = Handler(self.tmp_url, self.data, "ogv", **self.kw)
    self.file_detector = Magic(mime=True)

  def testConvertVideo(self):
    """Test coversion of video to another format"""
    output_data = self.input.convert("mpeg")
    file_format = self.file_detector.from_buffer(output_data)
    self.assertEquals(file_format, 'video/mpeg')

  def testgetMetadata(self):
    """Test if metadata is extracted from"""
    output_metadata = self.input.getMetadata()
    self.assertEquals(output_metadata, {'Encoder': 'Lavf52.64.2'})

  def testsetMetadata(self):
    """ Test if metadata are inserted correclty """
    metadata_dict = {"title": "Set Metadata Test", "creator": "cloudooo"}
    output = self.input.setMetadata(metadata_dict)
    handler = Handler(self.tmp_url, output, "ogv", **self.kw)
    metadata = handler.getMetadata()
    self.assertEquals(metadata["Title"], "Set Metadata Test")
    self.assertEquals(metadata["Creator"], "cloudooo")

  def testConvertAudio(self):
    """Test coversion of audio to another format"""
    self.data = open("./data/test.ogg").read()
    self.input = Handler(self.tmp_url, self.data, "ogg", **self.kw)
    output_data = self.input.convert("wav")
    file_format = self.file_detector.from_buffer(output_data)
    # XXX this might expect 'audio/vnd.wave' but magic only got 'audio/x-wav'
    self.assertEquals(file_format, 'audio/x-wav')


