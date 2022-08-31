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

from cloudooo.handler.ooo.document import FileSystemDocument, OdfDocument
from cloudooo.handler.ooo.handler import Handler
from cloudooo.handler.ooo.application.openoffice import OpenOffice
from cloudooo.manager import Manager
from cloudooo.handler.ooo.mimemapper import MimeMapper
from cloudooo.handler.ooo.filter import Filter
from cloudooo.handler.ooo.monitor.request import MonitorRequest
from cloudooo.interfaces.file import IFile, IOdfDocument
from cloudooo.interfaces.lockable import ILockable
from cloudooo.interfaces.manager import IManager
from cloudooo.interfaces.application import IApplication
from cloudooo.interfaces.filter import IFilter
from cloudooo.interfaces.mimemapper import IMimemapper
from cloudooo.interfaces.handler import IHandler
from cloudooo.interfaces.monitor import IMonitor
from cloudooo.interfaces.granulate import ITableGranulator, \
                                          IImageGranulator, \
                                          ITextGranulator
from cloudooo.tests.backportUnittest import TestCase, expectedFailure

import zope.interface.verify

class TestInterface(TestCase):
  """Test All Interfaces"""

  def testITableGranulator(self):
    """Test if Manager implements ITableGranulator"""
    zope.interface.verify.verifyClass(ITableGranulator, Manager)

  def testITextGranulator(self):
    """Test if Manager implements ITextGranulator"""
    zope.interface.verify.verifyClass(ITextGranulator, Manager)

  def testIImageGranulator(self):
    """Test if Manager implements IImageGranulator"""
    zope.interface.verify.verifyClass(IImageGranulator, Manager)

  def testIFile(self):
    """Test if FileSystemDocument implements IFile"""
    zope.interface.verify.verifyClass(IFile, FileSystemDocument)

  def testIOdfDocument(self):
    """Test if OdfDocument implements IOdfDocument"""
    zope.interface.verify.verifyClass(IOdfDocument, OdfDocument)

  def testIFilter(self):
    """Test if Filter implements IFile"""
    zope.interface.verify.verifyClass(IFilter, Filter)

  @expectedFailure
  def testIManager(self):
    """Test if Manager implements IManager"""
    zope.interface.verify.verifyClass(IManager, Manager)

  @expectedFailure
  def testIMimeMapper(self):
    """Test if Mimemapper implements IMimemapper."""
    zope.interface.verify.verifyClass(IMimemapper, MimeMapper)

  def testIMonitor(self):
    """Test if Monitors implements IMonitor"""
    zope.interface.verify.verifyClass(IMonitor, MonitorRequest)

  def testIHandler(self):
    """Test if Handlers implements IHandler"""
    zope.interface.verify.verifyClass(IHandler, Handler)

  def testIApplication(self):
    """Test if OpenOffice implements IApplication"""
    zope.interface.verify.verifyClass(IApplication, OpenOffice)

  def testILockable(self):
    """Test if Openoffice implements ILockable"""
    zope.interface.verify.verifyClass(ILockable, OpenOffice)
