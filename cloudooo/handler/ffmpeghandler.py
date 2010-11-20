##############################################################################
#
# Copyright (c) 2009-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Gabriel M. Monnerat <gabriel@tiolive.com>
#                    Rafael Monnerat <rafael@nexedi.com>
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

from zope.interface import implements
from cloudooo.interfaces.handler import IHandler
from cloudooo.document import FileSystemDocument


class FFMpegHandler:
  """For each Document inputed is created on instance of this class to
  manipulate the document. This Document must be able to create and remove a
  temporary document at FS, load, export and export.
  """
  implements(IHandler)

  def __init__(self, base_folder_url, data, **kw):
    """Creates document in file system and loads it in OOo."""
    self.document = FileSystemDocument(base_folder_url, data)

  def _getCommand(self, *args, **kw):
    """Transforms all parameters passed in a command"""
    return ""

  def convert(self, source_format=None, destination_format=None, **kw):
    """Executes a procedure in accordance with parameters passed."""
    return ""

  def getMetadata(self, converted_data=False):
    """Returns a dictionary with all metadata of document.
    Keywords Arguments:
    converted_data -- Boolean variable. if true, the document is also returned
    along with the metadata."""
    return {}

  def setMetadata(self, metadata):
    """Returns a document with new metadata.
    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    # Is it supportable?
    return ""
