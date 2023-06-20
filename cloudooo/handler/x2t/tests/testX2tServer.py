##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
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
import io
import zipfile
from base64 import decodebytes, encodebytes
from os.path import join

from cloudooo.tests.cloudoooTestCase import TestCase


class TestServer(TestCase):
  """Test XmlRpc Server. Needs cloudooo server started"""

  def ConversionScenarioList(self):
    return [
      # magic recognize xlsy and docy files as zip files, so the
      # expected mime is application/zip
      (join('data', 'test.xlsx'), "xlsx", "xlsy", "application/zip"),
      (join('data', 'test.xlsy'), "xlsy", "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
      (join('data', 'test_with_image.docx'), "docx", "docy", "application/zip"),
      (join('data', 'test_with_image.docy'), "docy", "docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ]

  def testConvertOnlyOfficeToFrom(self):
    """Converts xlsx,docx to their y format and y to x"""
    self.runConversionList(self.ConversionScenarioList())

  def FaultConversionScenarioList(self):
    scenario_list = [
      # Test to verify if server fail when a empty file is sent
      (b'', '', ''),
    ]
    # Try convert one xlsx for a invalid format
    with open(join('data', 'test.xlsx'), 'rb') as f:
      scenario_list.append((f.read(), 'xlsx', 'xyz'))
    return scenario_list

  def test_xlsx_to_xlsy(self):
    with open(join('data', 'test.xlsx'), 'rb') as f:
      xlsx_data = f.read()
    xlsy_data = self.proxy.convertFile(
      encodebytes(xlsx_data).decode(),
      'xlsx',
      'xlsy',
      False
    )
    self.assertEqual(
      sorted(zipfile.ZipFile(io.BytesIO(decodebytes(xlsy_data.encode()))).namelist()),
      sorted(['Editor.xlsx', 'body.txt', 'metadata.json'])
    )

  def test_docx_to_docy(self):
    with open(join('data', 'test_with_image.docx'), 'rb') as f:
      docx_data = f.read()
    docy_data = self.proxy.convertFile(
      encodebytes(docx_data).decode(),
      'docx',
      'docy',
      False
    )
    self.assertEqual(
      sorted(zipfile.ZipFile(io.BytesIO(decodebytes(docy_data.encode()))).namelist()),
      sorted(['body.txt', 'media/image1.png', 'metadata.json'])
    )

