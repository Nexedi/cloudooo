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
import sha
from cloudooo.handler.ffmpeg.handler import FFMPEGHandler
from cloudooo.handler.tests.handlerTestCase import HandlerTestCase


class TestFFMPEGHandler(HandlerTestCase):

  def setUp(self):
    self.data = open("./data/test.3gp").read()
    self.input = FFMPEGHandler("./data", self.data
                               ,"3gp")


  def testConvertVideo(self):
    """Test coversion of video to another format"""
    # XXX - Hash might use md5, but it does not work for string
    input_data = sha.new(self.data)
    hash_input = input_data.digest()
    output_data = self.input.convert("ogv")
    output = sha.new(output_data)
    hash_output = output.digest()
    self.assertTrue(hash_input != hash_output)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFFMPEGHandler))
  return suite
