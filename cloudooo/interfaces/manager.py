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

from zope.interface import Interface


class IManager(Interface):
  """Provides method to manipulate documents and metadatas using OOo"""

  def convertFile(file, source_format, destination_format, zip, refresh):
    """Returns the converted file in the given format.

    zip parameter can be specified to return the result of conversion
    in the form of a zip archive (which may contain multiple parts).
    This can be useful to convert a single ODF file to HTML
    and png images.
    """

  def getFileMetadataItemList(file, source_format, base_document):
    """Returns a list key, value pairs representing the
    metadata values for the document. The structure of this
    list is "unpredictable" and follows the convention of each file.
    """

  def updateFileMetadata(file, source_format, metadata_dict):
    """Updates the file in the given source_format with provided metadata and
    return the resulting new file."""

  def getAllowedExtensionList(request_dict):
    """Returns a list extension which can be generated from given extension or
    document type."""

  def granulateFile(file, source_format, zip):
    """Returns a zip file with parts of an document splited by grains."""


class IERP5Compatibility(Interface):
  """ Provides compatibility interface with ERP5 Project.
  This methods provide same API as OpenOffice.org project.
  XXX Unfinished Docstring.
  """

  def run_convert(filename, data, meta, extension, orig_format):
    """Returns the metadata and the ODF in dictionary"""
    return (200 or 402, dict(), '')

  def run_setmetadata(filename, data, meta, extension, orig_format):
    """Adds metadata in ODF and returns a new ODF with metadata in
    dictionary"""
    return (200 or 402, dict(), '')

  def run_getmetadata(self, filename, data, meta, extension, orig_format):
    """Extracts metadata from ODF and returns in dictionary"""
    return (200 or 402, dict(), '')

  def run_generate(filename, data, meta, extension, orig_format):
    """It exports a ODF to given format"""
    return (200 or 402, dict(), '')

  def getAllowedTargetItemList(self, content_type):
    """List types which can be generated from given content type"""
    return (200 or 402, dict(), '')
