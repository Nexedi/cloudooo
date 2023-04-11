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

import unittest
from cloudooo.interfaces.handler import IHandler
from cloudooo.handler.ffmpeg.handler import Handler


class TestInterface(unittest.TestCase):
  """Test IHandler Interface"""

  def testIHandler(self):
    """Test if Handlers implements IHandler"""
    self.assertTrue(IHandler.implementedBy(Handler))
    self.assertEqual(IHandler.get('convert').required, ('destination_format',))
    self.assertEqual(IHandler.get('getMetadata').required,
        ('converted_data',))
    self.assertEqual(IHandler.get('setMetadata').required,
        ('metadata_dict',))


