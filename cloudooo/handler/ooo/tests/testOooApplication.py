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
from cloudooo.handler.ooo.application.application import Application


class TestApplication(unittest.TestCase):

  def setUp(self):
    """Instantiate one application object and load settings on object"""
    self.application = Application()
    self.application.loadSettings('localhost', 9999, '/tmp/')

  def testLoadSettings(self):
    """Test if settings are defined correctly"""
    self.assertEquals(self.application.hostname, 'localhost')
    self.assertEquals(self.application.port, 9999)
    self.assertEquals(self.application.path_run_dir, '/tmp/')

  def testStartTimeout(self):
    """Test if the attribute timeout is defined correctly"""
    self.assertEquals(self.application.timeout, 20)
    application = Application()
    application.loadSettings('localhost', 9999, '/', start_timeout=25)
    self.assertEquals(application.timeout, 25)

  def testgetAddress(self):
    """Test if getAddress() returns tuple with address correctly """
    self.assertEquals(self.application.getAddress(), ('localhost', 9999))

  def testPid(self):
    """As the application do not have the pid() should return None"""
    self.assertEquals(self.application.pid(), None)


