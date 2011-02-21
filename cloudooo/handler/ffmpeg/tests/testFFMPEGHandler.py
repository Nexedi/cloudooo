##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Priscila Manhães  <psilva@iff.edu.br>
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
import md5
from cloudooo.handler.ffmpeg.handler import FFMPEGHandler


class TestFFMPEGHandler(unittest.TestCase):

  def testConvertVideo(self):
    """Test coversion of diferents formats of video"""
    input_data = FFMPEGHandler("tests/data",
                               open("tests/data/test.3gp").read())
    hash_input = input_data.digest()
    output_data = handler.convert("ogv")
    hash_output = output_data.digest()
    self.assertTrue(hash_input == hash_output)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFFMPEGHandler))
  return suite
