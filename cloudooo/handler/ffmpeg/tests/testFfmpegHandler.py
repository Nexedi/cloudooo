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
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################

from magic import Magic
from cloudooo.handler.ffmpeg.handler import Handler
from cloudooo.tests.handlerTestCase import HandlerTestCase


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
    self.assertEqual(file_format, 'video/mpeg')

  def testgetMetadata(self):
    """Test if metadata is extracted from"""
    output_metadata = self.input.getMetadata()
    self.assertEqual(output_metadata, {'Encoder': 'Lavf52.64.2'})

  def testsetMetadata(self):
    """ Test if metadata are inserted correclty """
    metadata_dict = {"title": "Set Metadata Test", "creator": "cloudooo"}
    output = self.input.setMetadata(metadata_dict)
    handler = Handler(self.tmp_url, output, "ogv", **self.kw)
    metadata = handler.getMetadata()
    self.assertEqual(metadata["Title"], "Set Metadata Test")
    self.assertEqual(metadata["Creator"], "cloudooo")

  def testConvertAudio(self):
    """Test coversion of audio to another format"""
    self.data = open("./data/test.ogg").read()
    self.input = Handler(self.tmp_url, self.data, "ogg", **self.kw)
    output_data = self.input.convert("wav")
    file_format = self.file_detector.from_buffer(output_data)
    # XXX this might expect 'audio/vnd.wave' but magic only got 'audio/x-wav'
    self.assertEqual(file_format, 'audio/x-wav')


