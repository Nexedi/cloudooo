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

# pylint:disable=no-method-argument,no-self-argument

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


class IDocumentGranulator(Interface):
  """Provides a method to granulate a document into grains (chunks of text
  with their location), for indexing and retrieval."""

  def granulateFile(file, source_format, granulate_kw):
    """Returns the list of grains of a document.

    file -- document encoded in base64
    source_format -- extension ("pdf", "html") or mimetype ("application/pdf",
      "text/html") of the document. PDF is read directly (with page
      information), HTML is parsed directly (without page information), any
      other format that can be converted to ODT is converted first.
    granulate_kw -- options:
      strategy -- "structure" (default: grains follow headings, tables are
        kept apart), "page" (grains do not cross pages), "fixed" (structure
        is ignored) or "blocks" (no packing, returns the text blocks)
      max_chars -- maximum size of a grain, 1500 by default
      overlap_chars -- text repeated at the start of a grain when a section is
        split because of max_chars, 200 by default
      include_tables -- False to leave tables out, True by default
      page_range -- [first, last] pages to process (starts at 1), to granulate
        a large document in several calls. PDF is read directly; other
        non-HTML formats are rendered as PDF to obtain page numbers. It is an
        error for HTML documents, which have no pages.

    Each grain is a dict with: index, text, context (titles of the enclosing
    sections joined with " > "), type ("text" or "table"), block_ids,
    char_count, content_hash (sha256 of text) and, for formats with pages,
    page_start and page_end.
    """
