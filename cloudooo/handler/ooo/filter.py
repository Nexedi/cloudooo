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

from zope.interface import implements
from cloudooo.interfaces.filter import IFilter


class Filter(object):
  """Filter of OOo."""

  implements(IFilter)

  def __init__(self, extension, filter, mimetype, document_service, **kwargs):
    """Receives extension, filter and mimetype of filter and saves in object.
    """
    self._extension = extension
    self._filter = filter
    self._mimetype = mimetype
    self._document_service = document_service
    self._preferred = kwargs.get('preferred')
    self._sort_index = kwargs.get('sort_index')
    self._label = kwargs.get("label")

  def getLabel(self):
    """Returns label."""
    return self._label

  def getSortIndex(self):
    """Returns sort index."""
    return self._sort_index

  def isPreferred(self):
    """Check if this filter is preferred."""
    return self._preferred

  def getName(self):
    """Returns name of filter."""
    return self._filter

  def getDocumentService(self):
    """Returns the type of document that can use this filter."""
    return self._document_service

  def getExtension(self):
    """Returns extension as string."""
    return self._extension

  def getMimetype(self):
    """Returns mimetype."""
    return self._mimetype
