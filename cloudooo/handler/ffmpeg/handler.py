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
from cloudooo.interfaces.handler import IHandler
from cloudooo.file import File
from cloudooo.util import logger
from subprocess import Popen, PIPE
from tempfile import mktemp

class Handler(object):
  """FFMPEG Handler is used to handler inputed audio and video files"""

  implements(IHandler)

  def __init__(self, base_folder_url, data, source_format, **kw):
    """
    base_folder_url(string)
      The requested url for data base folder
    data(string)
      The opened and readed file into a string
    source_format(string)
      The source format of the inputed file"""
    self.base_folder_url = base_folder_url
    self.input = File(base_folder_url, data, source_format)
    self.environment = kw.get("env", {})

  def convert(self, destination_format):
    """ Convert the inputed file to output as format that were informed """
    # XXX This implementation could use ffmpeg -i pipe:0, but
    # XXX seems super unreliable currently and it generates currupted files in
    # the end
    logger.debug("FfmpegConvert: %s > %s" % (self.input.source_format, destination_format))
    output_url = mktemp(suffix=".%s" % destination_format,
                        dir=self.input.directory_name)
    command = ["ffmpeg",
               "-i",
               self.input.getUrl(),
               "-y",
               output_url]
    # XXX ffmpeg has a bug that needs this options to work with webm format
    if destination_format == "webm":
      command.insert(3, "32k")
      command.insert(3, "-ab")
    try:
      stdout, stderr = Popen(command,
                             stdout=PIPE,
                             stderr=PIPE,
                             close_fds=True,
                             env=self.environment).communicate()
      self.input.reload(output_url)
      if len(self.input.getContent()) == 0:
        logger.error(stderr.split("\n")[-2])
      return self.input.getContent()
    finally:
      self.input.trash()

  def getMetadata(self, base_document=False):
    """Returns a dictionary with all metadata of the file.
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
        metadata_dict[key.strip().capitalize()] = value.strip()
    self.input.trash()
    return metadata_dict

  def setMetadata(self, metadata_dict={}):
    """Returns a document with new metadata.
    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    output_url = mktemp(suffix=".%s" % self.input.source_format,
                        dir=self.input.directory_name)
    command = ["ffmpeg",
               "-i",
               self.input.getUrl(),
               "-y",
               output_url]
    for metadata in metadata_dict:
      command.insert(3, "%s=%s"%(metadata, metadata_dict[metadata]))
      command.insert(3, "-metadata")
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

  @staticmethod
  def getAllowedConversionFormatList(source_mimetype):
    """Returns a list content_type and their titles which are supported
    by enabled handlers.

    [('audio/ogg;codecs=opus', 'Opus Audio File Format'),
     ('video/webm', 'Webm Video File Format'),
     ...
    ]
    """
    # XXX NotImplemented
    return []
