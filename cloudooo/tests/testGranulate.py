##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Hugo H. Maia Vieira <hugomaia@tiolive.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
from cloudoooTestCase import cloudoooTestCase, make_suite
from cloudooo.manager import Manager


class TestGranulate(cloudoooTestCase):

  def testGranulateFile(self):
    """Test if the granulateFile returns the grains correctly"""
    manager = Manager('some/path')
    self.assertRaises(NotImplementedError, manager.granulateFile, 'some/file',
                                                                  'odt')


def test_suite():
  return make_suite(TestGranulate)

if __name__ == "__main__":
  suite = unittest.TestLoader().loadTestsFromTestCase(TestGranulate)
  unittest.TextTestRunner(verbosity=2).run(suite)
