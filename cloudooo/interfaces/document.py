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
from zope.interface import Attribute


class IDocument(Interface):
  """Manipulates documents in file system"""

  base_folder_url = Attribute("Url of folder that is used to create temporary \
                              files")
  directory_name = Attribute("String of directory name")
  source_format = Attribute("Document Extension")
  url = Attribute("Complete path of document in file system")
  original_data = Attribute("Original data")

  def load():
    """From the data creates one archive into file system using original data"""

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
