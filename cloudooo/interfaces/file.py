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

from zope.interface import Interface
from zope.interface import Attribute


class IFile(Interface):
  """Manipulates documents in file system"""

  base_folder_url = Attribute("Url of folder that is used to create temporary \
                              files")
  directory_name = Attribute("String of directory name")
  source_format = Attribute("Document Extension")
  url = Attribute("Complete path of document in file system")
  original_data = Attribute("Original data")

  def load():
    """From the data creates one archive into file system using original data
    """

  def reload(url):
    """In the case of another file with the same content be created, pass the
    url to load the new file"""

  def getContent(zip):
    """Returns data of document"""

  def getUrl():
    """Get the url of temporary file in file system"""

  def trash():
    """Remove the file in file system"""

  def restoreOriginal():
    """Restore the document with the original document"""


class IOdfDocument(Interface):
  """Manipulates odf documents in memory"""

  source_format = Attribute("Document Extension")
  parsed_content = Attribute("Content.xml parsed with lxml")

  def getContentXml():
    """Returns the content.xml file as string"""

  def getFile(path):
    """Returns, as string, the file located in the given path, inside de odf
       file"""
