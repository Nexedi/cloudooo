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
  """Provides public method to communicate with Cloudooo clients
  """

  def convertFile(content, source_mimetype, destination_mimetype, **kw):
    """Returns the converted file in the given format.

    content : binary data to convert
    source_mimetype : mimetype of given content
    destination_mimetype : expected output conversion mimetype

    **kw holds specific parameters for the conversion
    """

  def convertBundle(content, filename, source_mimetype, destination_mimetype,
                    **kw):
    """The content must be a zip archive with multiples files.
    filename is the authority file to convert inside archive.
    All other files are embedded object usefull to perform the conversion
    like css, images, videos, audio files, ...
    It returns the converted data.

    content : zip bundle
    filename: filename of authority file to extract from the bundle.
    source_mimetype : mimetype of given authority file
    destination_mimetype : expected output conversion mimetype

    **kw holds specific parameters for the conversion
    """

  def getFileMetadataItemList(content, source_mimetype):
    """Returns a list key, value pairs representing the
    metadata values for the document. The structure of this
    list is "unpredictable" and follows the convention of each file.

    content : binary data where to reads metadata
    source_mimetype : mimetype of given content
    """

  def convertFileAndGetMetadataItemList(content, source_mimetype,
                                            destination_mimetype, **kw):
    """returns a converted version of provided content plus a
    dictionary of extracted metadata.
    signature of method is same as convertFile

    result is a json dictionary with 'conversion' and
    'metadata' entries.
    """

  def updateFileMetadata(content, source_mimetype, metadata_dict):
    """Updates the content with provided metadata and
    return the new file.

    content : binary data to convert
    source_mimetype : mimetype of given content
    metadata_dict : Metadatas to include in content
    """

  def getAllowedConversionFormatList(source_mimetype):
    """Returns a list content_type and their titles which are supported
    by enabled handlers.

    [('application/vnd.oasis.opendocument.text', 'ODF Text Document'),
     ('application/pdf', 'PDF - Portable Document Format'),
     ...
    ]
    """

  def getAllowedConversionFormatInfoList(source_mimetype):
    """Returns a list content_type and list of parameter which are supported
    by enabled handlers.

    (see IMimemapper.getAllowedExtensionInfoList)
    """

  def granulateFile(content, source_mimetype):
    """Returns a zip file with parts of an document splited by grains.
    """


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
