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
