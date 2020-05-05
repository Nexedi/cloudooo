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

from zope.interface import Interface


class ITableGranulator(Interface):
  """Provides methods to granulate a document into tables.
  """

  def getTableItemList(content, source_mimetype):
    """Returns the list of table IDs in the form of (id, title).
    """

  def getTable(content, source_mimetype, table_id ):
    """Returns the table into a new 'format' file.
    """

  def getColumnItemList(content, source_mimetype, table_id):
    """Return the list of columns in the form of (id, title).
    """

  def getLineItemList(content, source_mimetype, table_id):
    """Returns the lines of a given table as (key, value) pairs.
    """


class IImageGranulator(Interface):
  """Provides methods to granulate a document into images.
  """

  def getImageItemList(content, source_mimetype):
    """Return the list of images in the form of (id, title).
    """

  def getImage(content, filename, source_mimetype,
               destination_mimetype=None, **kw):
    """Return the given image.
    """


class ITextGranulator(Interface):
  """Provides methods to granulate a document into chapters and paragraphs.
  """

  def getParagraphItemList(content, source_mimetype):
    """Returns the list of paragraphs in the form of (id, class) where class
    may have special meaning to define TOC/TOI.
    """

  def getParagraph(content, source_mimetype, paragraph_id):
    """Returns the paragraph in the form of (text, class).
    """

  def getChapterItemList(content, source_mimetype):
    """Returns the list of chapters in the form of (id, level).
    """

  def getChapterItem(content, source_mimetype, chapter_id):
    """Return the chapter in the form of (title, level).
    """
