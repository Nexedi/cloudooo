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


import magic
from cloudooo.handler.imagemagick.handler import Handler
from cloudooo.tests.handlerTestCase import HandlerTestCase


class TestHandler(HandlerTestCase):

  def afterSetUp(self):
    self.kw = dict(env=dict(PATH=self.env_path))

  def testConvertPNGtoJPG(self):
    """Test conversion of png to jpg"""
    png_file = open("data/test.png").read()
    handler = Handler(self.tmp_url, png_file, "png", **self.kw)
    jpg_file = handler.convert("jpg")
    mime = magic.Magic(mime=True)
    jpg_mimetype = mime.from_buffer(jpg_file)
    self.assertEquals("image/jpeg", jpg_mimetype)

  def testgetMetadataFromImage(self):
    """Test if metadata is extracted from image correctly"""
    png_file = open("data/test.png").read()
    handler = Handler(self.tmp_url, png_file, "png", **self.kw)
    metadata = handler.getMetadata()
    self.assertEquals(metadata.get("Compression"), "Zip")
    self.assertEquals(metadata.get("Colorspace"), "sRGB")
    self.assertEquals(metadata.get("Alpha color"), "grey74")

  def testsetMetadata(self):
    """ Test if metadata are inserted correclty """
    handler = Handler(self.tmp_url, "", "png", **self.kw)
    self.assertRaises(NotImplementedError, handler.setMetadata)


