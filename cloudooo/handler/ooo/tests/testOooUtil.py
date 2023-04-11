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
import logging
from cloudooo import util
import mimetypes


class TestUtil(unittest.TestCase):
  """Test Utils"""

  def testLog(self):
    """Instanciate Log and test __call__ called function log"""
    util.configureLogger(logging.DEBUG)
    util.logger.info("Test Log")
    util.logger.debug("Test Log")
    util.configureLogger(logging.INFO)
    util.logger.info("Test Log")
    util.logger.debug("Test Log")

  def testLoadMimetypelist(self):
    """Test if the file with mimetypes is loaded correctly"""
    self.assertEqual(mimetypes.types_map.get(".ogv"), None)
    self.assertEqual(mimetypes.types_map.get(".3gp"), None)
    util.loadMimetypeList()
    self.assertEqual(mimetypes.types_map.get(".ogv"), "video/ogg")
    self.assertEqual(mimetypes.types_map.get(".3gp"), "video/3gpp")


