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

from os.path import join
from cloudooo.tests.cloudoooTestCase import TestCase
from cloudooo.tests.backportUnittest import skip


class TestAllSupportedFormat(TestCase):

  def ConversionScenarioList(self):
    return [# XXX This might expect audio/octet-stream but only got audio/mpeg
            (join('data', 'test.ogg'), "ogg", "mp3", "audio/mpeg"),
            (join('data', 'test.ogg'), "ogg", "wav", "audio/x-wav"),
            ]

  def testAllSupportedFormat(self):
    """Test all audio types supported by ffmpeg"""
    self.runConversionList(self.ConversionScenarioList())

  @skip('FFMPEG does not support midi files anymore')
  def testMidi(self):
    """Tests if ffmpeg convets midi file"""
    self.runConversionList(join('data', 'test.ogg'), "ogg", "midi", "audio/rtp-midi")

