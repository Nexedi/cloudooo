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

from zope.interface import implements
from zipfile import ZipFile
from StringIO import StringIO
from lxml import etree
from cloudooo.interfaces.file import IOdfDocument
from cloudooo.file import File


class FileSystemDocument(File):
  pass


class OdfDocument(object):
  """Manipulates odf documents in memory"""

  implements(IOdfDocument)

  def __init__(self, data, source_format):
    """Open the the file in memory.

    Keyword arguments:
    data -- Content of the document
    source_format -- Document Extension
    """
    self._zipfile = ZipFile(StringIO(data))

    self.source_format = source_format
    # XXX - Maybe parsed_content should not be here, but on OOGranulate
    self.parsed_content = etree.fromstring(self.getContentXml())

  def getContentXml(self):
    """Returns the content.xml file as string"""
    return self._zipfile.read('content.xml')

  def getFile(self, path):
    """If exists, returns file as string, else return an empty string"""
    try:
      return self._zipfile.read(path)
    except KeyError:
      return ''

  def trash(self):
    """Remove the file in memory."""
    self._zipfile.close()
