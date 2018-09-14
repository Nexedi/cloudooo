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

from os.path import join
from cloudooo.tests.cloudoooTestCase import TestCase, make_suite

class TestServer(TestCase):
  """Test XmlRpc Server. Needs cloudooo server started"""

  def ConversionScenarioList(self):
    return [
            (join('data', 'test.ogv'), "ogv", "mpeg", "video/mpeg"),
            ]

  def testConvertVideo(self):
    """Converts ogv video to mpeg format"""
    self.runConversionList(self.ConversionScenarioList())

  def FaultConversionScenarioList(self):
    return [
            # Test to verify if server fail when a empty string is sent
            ('', '', ''),
            # Try convert one video for a invalid format
            (open(join('data', 'test.ogv')).read(), 'ogv', 'xyz'),
            # Try convert one video to format not possible
            (open(join('data', 'test.ogv')).read(), 'ogv', 'moov'),
            ]

  def testFaultConversion(self):
    """Test fail convertion of Invalid video files"""
    self.runFaultConversionList(self.FaultConversionScenarioList())

  def GetMetadataScenarioList(self):
    return [
            (join('data', 'test.ogv'), "ogv", dict(Data='', Encoder='Lavf52.64'+
            '.2')),
            ]

  def testGetMetadata(self):
    """test if metadata are extracted correctly from video file"""
    self.runGetMetadataList(self.GetMetadataScenarioList())

  def FaultGetMetadataScenarioList(self):
    return [
            # Test to verify if server fail when a empty string is sent
            ('', ''),
            ]

  def testFaultGetMetadata(self):
    """Test getMetadata from invalid video files"""
    self.runFaultGetMetadataList(self.FaultGetMetadataScenarioList())


  def UpdateMetadataScenarioList(self):
    return [
            (join('data', 'test.ogv'), "ogv", dict(Title='Server Set Metadata '+
            'Test')),
            ]

  def testSetMetadata(self):
    """Test if metadata is inserted correctly into video files"""
    self.runUpdateMetadataList(self.UpdateMetadataScenarioList())

