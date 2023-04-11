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

import unittest
from cloudooo.handler.ooo.filter import Filter


class TestFilter(unittest.TestCase):
  """Test filter and your interface"""

  def setUp(self):
    """Instatiated Filter with properties"""
    extension = 'pdf'
    filter = 'writer_pdf_Export'
    mimetype = 'application/pdf'
    document_type = "text"
    preferred = True
    sort_index = 1000
    self.filter = Filter(extension, filter, mimetype, document_type,
        preferred=preferred, sort_index=sort_index)

  def testFilter(self):
    """Tests filter gets"""
    self.assertEqual(self.filter.getExtension(), 'pdf')
    self.assertEqual(self.filter.getName(), 'writer_pdf_Export')
    self.assertEqual(self.filter.getMimetype(), 'application/pdf')
    self.assertEqual(self.filter.getSortIndex(), 1000)
    self.assertTrue(self.filter.isPreferred())


