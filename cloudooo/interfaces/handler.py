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

class IHandler(Interface):
  """Handles communications between manager and specific backends
  """

  def convert(destination_mimetype):
    """Convert to expected format
    """

  def getMetadata():
    """Returns a dictionary with all metadata of document.
    """

  def setMetadata(metadata_dict):
    """Returns a document with the new metadata
    """

  def getAllowedConversionFormatList(self, source_mimetype):
    """Returns a list content_type and their titles which are supported
    by enabled handlers.

    [('application/vnd.oasis.opendocument.text', 'ODF Text Document'),
     ('application/pdf', 'PDF - Portable Document Format'),
     ...
    ]
    """
