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
from cloudooo.handler.tests.handlerTestCase import make_suite


class TestInterface(unittest.TestCase):
  """Test All Interfaces"""

  def testITableGranulator(self):
    """Test if Manager implements ITableGranulator"""
    self.assertTrue(ITableGranulator.implementedBy(Manager))
    method_list = ['getLineItemList',
                   'getTable',
                   'getTableItemList',
                   'getColumnItemList']
    self.assertEquals(sorted(ITableGranulator.names()), sorted(method_list))

  def testITextGranulator(self):
    """Test if Manager implements ITextGranulator"""
    self.assertTrue(ITextGranulator.implementedBy(Manager))
    method_list = ['getChapterItemList',
                   'getParagraph',
                   'getChapterItem',
                   'getParagraphItemList']
    self.assertEquals(ITextGranulator.names(), method_list)

  def testIImageGranulator(self):
    """Test if Manager implements IImageGranulator"""
    self.assertTrue(IImageGranulator.implementedBy(Manager))
    method_list = ['getImageItemList', 'getImage']
    self.assertEquals(IImageGranulator.names(), method_list)

  def testIFile(self):
    """Test if FileSystemDocument implements IFile"""
    self.assertTrue(IFile.implementedBy(FileSystemDocument))

  def testIOdfDocument(self):
    """Test if OdfDocument implements IOdfDocument"""
    self.assertTrue(IOdfDocument.implementedBy(OdfDocument))
    method_list = ['getContentXml',
                   'parsed_content',
                   'source_format',
                   'getFile']
    self.assertEquals(IOdfDocument.names(), method_list)

  def testIFilter(self):
    """Test if Filter implements IFile"""
    self.assertTrue(IFilter.implementedBy(Filter))
    self.assertEquals(IFilter.names(), ['getLabel', 'getName', 'getSortIndex',
      'isPreferred', 'getDocumentService', 'getExtension', 'getMimetype'])

  def testIManager(self):
    """Test if Manager implements IManager"""
    self.assertTrue(IManager.implementedBy(Manager))
    method_list = ['convertFile',
                  'getFileMetadataItemList',
                  'updateFileMetadata',
                  'getAllowedExtensionList',
                  'granulateFile']

    for method in method_list:
      self.assertTrue(method in IManager.names())
    self.assertEquals(len(method_list), len(IManager.names()))

    self.assertEquals(IManager.get('convertFile').required, ('file',
      'source_format', 'destination_format', 'zip', 'refresh'))
    self.assertEquals(IManager.get('getAllowedExtensionList').required,
        ('request_dict',))
    self.assertEquals(IManager.get('getFileMetadataItemList').required,
        ('file', 'source_format', 'base_document'))
    self.assertEquals(IManager.get('updateFileMetadata').required,
        ('file', 'source_format', 'metadata_dict'))

  def testIMimeMapper(self):
    """Test if Mimemapper implements IMimemapper."""
    method_list = ['getDocumentTypeDict', 'getFilterName', 'loadFilterList',
        'getFilterList', 'getAllowedExtensionList',
        'isLoaded']
    for method in method_list:
      self.assertTrue(method in IMimemapper.names())

    self.assertTrue(IMimemapper.implementedBy(MimeMapper))
    self.assertEquals(len(method_list), len(IMimemapper.names()))
    self.assertEquals(IMimemapper.get('getFilterName').required,
                                  ('extension', 'document_type'))
    self.assertEquals(IMimemapper.get('loadFilterList').required, ())
    self.assertEquals(IMimemapper.get('getFilterList').required, ('extension',))
    self.assertEquals(IMimemapper.get('getDocumentTypeDict').required, ())
    self.assertEquals(IMimemapper.get('getAllowedExtensionList').required,
        ("document_type",))

  def testIMonitor(self):
    """Test if Monitors implements IMonitor"""
    self.assertTrue(IMonitor.implementedBy(MonitorRequest))
    self.assertEquals(IMonitor.names(), ["run"])

  def testIHandler(self):
    """Test if Handlers implements IHandler"""
    self.assertTrue(IHandler.implementedBy(Handler))
    method_list = ['convert', 'getMetadata', 'setMetadata']
    for method in method_list:
      self.assertTrue(method in IHandler.names(),
                            "Method %s is not declared" % method)
    self.assertEquals(len(method_list), len(IHandler.names()))
    self.assertEquals(IHandler.get('convert').required, ('destination_format',))
    self.assertEquals(IHandler.get('getMetadata').required,
        ('converted_data',))
    self.assertEquals(IHandler.get('setMetadata').required,
        ('metadata_dict',))

  def testIApplication(self):
    """Test if OpenOffice implements IApplication"""
    self.assertTrue(IApplication.implementedBy(OpenOffice))
    application_method_list = ["start", "stop", "pid",
                              "status", "restart",
                              "loadSettings", "getAddress"]
    self.assertEquals(sorted(IApplication.names()),
        sorted(application_method_list))

  def testILockable(self):
    """Test if Openoffice implements ILockable"""
    self.assertTrue(ILockable.implementedBy(OpenOffice))
    lockable_method_list = ["_lock", "acquire", "release", "isLocked"]
    self.assertEquals(sorted(ILockable.names()), sorted(lockable_method_list))


def test_suite():
  return make_suite(TestInterface)
