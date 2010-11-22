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

from zope.interface import implements
from cloudooo.interfaces.granulate import ITableGranulator, \
                                          IImageGranulator, \
                                          ITextGranulator


class OOGranulate(object):
  """Granulate an OpenOffice document into tables, images, chapters and
  paragraphs."""

  implements(ITableGranulator, IImageGranulator, ITextGranulator)

  def getTableItemList(self, file):
    """Returns the list of table IDs in the form of (id, title)."""
    raise NotImplementedError

  def getColumnItemList(self, file, table_id):
    """Return the list of columns in the form of (id, title)."""
    raise NotImplementedError

  def getLineItemList(self, file, table_id):
    """Returns the lines of a given table as (key, value) pairs."""
    raise NotImplementedError

  def getImageItemList(self, file):
    """Return the list of images in the form of (id, title)."""
    raise NotImplementedError

  def getImage(self, file, image_id, format=None, resolution=None, **kw):
    """Return the given image."""
    raise NotImplementedError

  def getParagraphItemList(self, file):
    """Returns the list of paragraphs in the form of (id, class) where class
    may have special meaning to define TOC/TOI."""
    raise NotImplementedError

  def getParagraphItem(self, file, paragraph_id):
    """Returns the paragraph in the form of (text, class)."""
    raise NotImplementedError

  def getChapterItemList(self, file):
    """Returns the list of chapters in the form of (id, level)."""
    raise NotImplementedError

  def getChapterItem(self, file, chapter_id):
    """Return the chapter in the form of (title, level)."""
    raise NotImplementedError
