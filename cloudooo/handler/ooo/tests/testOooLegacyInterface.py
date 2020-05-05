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

from base64 import encodestring
from cloudooo.tests.cloudoooTestCase import TestCase, make_suite
from pkg_resources import resource_filename


class TestLegacyInterface(TestCase):

  def testHtmlToBaseFormatConversion(self):
    """Check implicit base conversion of HTML documents."""
    filename = resource_filename('cloudooo.handler.ooo.tests.data',
                                 'test_failure_conversion.html')
    data =  open(filename, 'r').read()
    status, response_dict, message = self.proxy.run_convert(
                                                  filename,
                                                  encodestring(data),
                                                  None,
                                                  None,
                                                  'text/html')

    self.assertEquals(response_dict['mime'], 'text/html')
    self.assertEquals(self._getFileType(response_dict['data']),
                      'text/html')

  def testHtmlToOdt(self):
    """Check conversion of HTML to odt"""
    filename = resource_filename('cloudooo.handler.ooo.tests.data',
                                 'test_failure_conversion.html')
    data =  open(filename, 'r').read()
    status, response_dict, message = self.proxy.run_generate(filename,
                                                             encodestring(data),
                                                             None,
                                                             'odt',
                                                             'text/html')
    self.assertEquals(response_dict['mime'], 'application/vnd.oasis.opendocument.text')
    self.assertEquals(self._getFileType(response_dict['data']),
                      'application/vnd.oasis.opendocument.text')

