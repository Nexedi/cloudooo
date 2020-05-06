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
from cloudooo.tests.cloudoooTestCase import TestCase, make_suite

class TestAllSupportedFormat(TestCase):

  def ConversionScenarioList(self):
    return [
            # XXX this might expect 'video/avi' but magic only got
            # 'video/x-msvideo'
            (join('data', 'test.ogv'), "ogv", "avi", "video/x-msvideo"),
            # XXX this might expect 'application/x-shockwave-flash' but magic
            # only got 'video/x-flv'
            (join('data', 'test.ogv'), "ogv", "flv", "video/x-flv"),
            # XXX This might expect video/x-matroska but only
            # got application/octet-stream
            (join('data', 'test.ogv'), "ogv", "mkv", "application/octet-stream"),
            (join('data', 'test.ogv'), "ogv", "mp4", "video/mp4"),
            (join('data', 'test.ogv'), "ogv", "mpeg", "video/mpeg"),
            (join('data', 'test.ogv'), "ogv", "webm", "video/webm"),
            ]

  def testAllSupportedFormat(self):
    self.runConversionList(self.ConversionScenarioList())

