##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Priscila Manhaes  <psilva@iff.edu.br>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
from cloudooo.interfaces.handler import IHandler
from cloudooo.file import File
from subprocess import Popen, PIPE
from tempfile import mktemp


class Handler(object):
  """FFMPEG Handler is used to handler inputed video files"""

  implements(IHandler)

  def __init__(self, base_folder_url, data, source_format, **kw):
    """
    base_folder_url(string)
      The requested url for data base folder
    data(string)
      The opened and readed video into a string
    source_format(string)
      The source format of the inputed video"""
    self.base_folder_url = base_folder_url
    self.input = File(base_folder_url, data, source_format)
    self.environment = kw.get("env", {})

  def convert(self, destination_format):
    """ Convert the inputed video to output as format that were informed """
    # XXX This implementation could use ffmpeg -i pipe:0, but
    # XXX seems super unreliable currently and it generates currupted files in
    # the end
    output_url = mktemp(suffix=".%s" % destination_format,
                        dir=self.input.directory_name)
    command = ["ffmpeg",
               "-i",
               self.input.getUrl(),
               "-y",
               output_url]
    try:
      stdout, stderr = Popen(command,
                             stdout=PIPE,
                             stderr=PIPE,
                             close_fds=True,
                             env=self.environment).communicate()
      self.input.reload(output_url)
      return self.input.getContent()
    finally:
      self.input.trash()

  def getMetadata(self, base_document=False):
    """Returns a dictionary with all metadata of the video.
    Keywords Arguments:"""
    command = ["ffprobe",self.input.getUrl()]
    stdout, stderr =  Popen(command,
                           stdout=PIPE,
                           stderr=PIPE,
                           close_fds=True,
                           env=self.environment).communicate()
    metadata = stderr.split('Metadata:')[1].split('\n')
    metadata_dict = {}
    for data in metadata:
      if len(data) != 0:
        key, value = data.split(':')
        metadata_dict[key.strip()] = value.strip()
    self.input.trash()
    return metadata_dict

  def setMetadata(self, metadata={}):
    """Returns a document with new metadata.
    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    raise NotImplementedError
