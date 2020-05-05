##############################################################################
#
# Copyright (c) 2009-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Gabriel M. Monnerat <gabriel@tiolive.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
from cloudooo.tests.cloudoooTestCase import TestCase, make_suite


class TestServer(TestCase):
  """Test XmlRpc Server. Needs cloudooo server started"""

  def ConversionScenarioList(self):
    return [
            (join('data', 'test.pdf'), "pdf", "txt", "text/plain"),
            ]

  def testConvertPDFtoTxt(self):
    """Converts pdf to txt"""
    self.runConversionList(self.ConversionScenarioList())

  def FaultConversionScenarioList(self):
    return [
            # Test to verify if server fail when a empty string is sent
            ('', '', ''),
            # Try convert one video for a invalid format
            (open(join('data', 'test.pdf')).read(), 'pdf', 'xyz'),
            # Try convert one video to format not possible
            (open(join('data', 'test.pdf')).read(), 'pdf', 'ogv'),
            ]

  def testFaultConversion(self):
    """Test fail convertion of Invalid pdf files"""
    self.runFaultConversionList(self.FaultConversionScenarioList())


  def GetMetadataScenarioList(self):
    return [
            (join('data', 'test.pdf'), "pdf", dict(title='Free Cloud Alliance'+
            ' Presentation')),
            ]

  def testGetMetadataFromPdf(self):
    """test if metadata are extracted correctly from pdf files"""
    self.runGetMetadataList(self.GetMetadataScenarioList())

  def FaultGetMetadataScenarioList(self):
    return [
            # Test to verify if server fail when a empty string is sent
            ('', ''),
            ]

  def testFaultGetMetadata(self):
    """Test getMetadata from invalid pdf file"""
    self.runFaultGetMetadataList(self.FaultGetMetadataScenarioList())

  def UpdateMetadataScenarioList(self):
    return [
            (join('data', 'test.pdf'), "pdf", dict(producer='Cloudooo')),
            ]

  def testSetMetadata(self):
    """Test if metadata is inserted correctly in pdf file"""
    self.runUpdateMetadataList(self.UpdateMetadataScenarioList())

