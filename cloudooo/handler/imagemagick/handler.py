##############################################################################
#
# Copyright (c) 2009-2011 Nexedi SA and Contributors. All Rights Reserved.
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

import re
from zope.interface import implements
from cloudooo.interfaces.handler import IHandler
from cloudooo.file import File
from cloudooo.util import logger
from subprocess import Popen, PIPE
from tempfile import mktemp


class Handler(object):
  """ImageMagic Handler is used to handler images."""

  implements(IHandler)

  def __init__(self, base_folder_url, data, source_format, **kw):
    """ Load pdf document """
    self.base_folder_url = base_folder_url
    self.file = File(base_folder_url, data, source_format)
    self.environment = kw.get("env", {})

  def convert(self, destination_format=None, **kw):
    """Convert a image"""
    logger.debug("ImageMagickConvert: %s > %s" % (self.file.source_format, destination_format))
    output_url = mktemp(suffix='.%s' % destination_format,
                        dir=self.base_folder_url)
    command = ["convert", self.file.getUrl(), output_url]
    stdout, stderr = Popen(command,
                          stdout=PIPE,
                          stderr=PIPE,
                          close_fds=True,
                          env=self.environment).communicate()
    self.file.reload(output_url)
    try:
      return self.file.getContent()
    finally:
      self.file.trash()

  def getMetadata(self, base_document=False):
    """Returns a dictionary with all metadata of document.
    along with the metadata.
    """
    command = ["identify", "-verbose", self.file.getUrl()]
    stdout, stderr = Popen(command,
                          stdout=PIPE,
                          stderr=PIPE,
                          close_fds=True,
                          env=self.environment).communicate()
    self.file.trash()
    metadata_dict = {}
    for std in stdout.split("\n"):
      std = std.strip()
      if re.search("^[a-zA-Z]", std):
        if std.count(":") > 1:
          key, value = re.compile(".*\:\ ").split(std)
        else:
          key, value = std.split(":")
        metadata_dict[key] = value.strip()
    return metadata_dict

  def setMetadata(self, metadata={}):
    """Returns image with new metadata.
    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    raise NotImplementedError

  @staticmethod
  def getAllowedConversionFormatList(source_mimetype):
    """Returns a list content_type and their titles which are supported
    by enabled handlers.

    [('image/jpeg', 'Jpeg Image File Format'),
     ('image/png', 'Png Image File Format'),
     ...
    ]
    """
    # XXX NotImplemented
    return []
