##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Hugo H. Maia Vieira <hugomaia@tiolive.com>
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


class ITableGranulator(Interface):
  """Provides methods to granulate a document into tables."""

  def getTableItemList(data, source_format):
    """Returns the list of table IDs in the form of (id, title)."""

  def getTableItem(data, format, table_id, source_format):
    """Returns the table into a new 'format' file."""

  def getTableMatrix(self, table_id, source_format):
    """Returns the table as a matrix."""

  def getColumnItemList(data, table_id, source_format):
    """Return the list of columns in the form of (id, title)."""

  def getLineItemList(data, table_id, source_format):
    """Returns the lines of a given table as (key, value) pairs."""


class IImageGranulator(Interface):
  """Provides methods to granulate a document into images."""

  def getImageItemList(data, source_format):
    """Return the list of images in the form of (id, title)."""

  def getImage(data, image_id, source_format, format=None, resolution=None, **kw):
    """Return the given image."""


class ITextGranulator(Interface):
  """Provides methods to granulate a document into chapters and paragraphs."""

  def getParagraphItemList(data, source_format):
    """Returns the list of paragraphs in the form of (id, class) where class
    may have special meaning to define TOC/TOI."""

  def getParagraphItem(data, paragraph_id, source_format):
    """Returns the paragraph in the form of (text, class)."""

  def getChapterItemList(data, source_format):
    """Returns the list of chapters in the form of (id, level)."""

  def getChapterItem(data, chapter_id, source_format):
    """Return the chapter in the form of (title, level)."""
