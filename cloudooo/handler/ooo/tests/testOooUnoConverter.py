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

import json
import magic
import pkg_resources
from subprocess import Popen, PIPE
from os.path import exists, join
from cloudooo.tests.handlerTestCase import HandlerTestCase
from cloudooo.handler.ooo.application.openoffice import openoffice
from cloudooo.handler.ooo.document import FileSystemDocument

OPENOFFICE = True


class TestUnoConverter(HandlerTestCase):
  """Test case to test all features of the unoconverter script"""

  file_msg_list = ["Microsoft Office Document",
                  "CDF V2 Document, Little Endian, Os: Windows, Version 1.0,"]

  def afterSetUp(self):
    """ """
    openoffice.acquire()
    self.hostname, self.port = openoffice.getAddress()
    data = open("data/test.odt", 'r').read()
    self.document = FileSystemDocument(self.tmp_url, data, 'odt')

  def tearDown(self):
    """Called to unlock the openoffice"""
    openoffice.release()

  def testUnoConverterOdtToDoc(self):
    """Test script unoconverter"""
    mimemapper = dict(filter_list=[('doc',
                                    'com.sun.star.text.TextDocument',
                                    'MS Word 97')],
                     doc_type_list_by_extension=dict(doc=['com.sun.star.text.TextDocument']))
    mimemapper_pickled = json.dumps(mimemapper)
    python = join(self.office_binary_path, "python")
    command = [exists(python) and python or "python",
          pkg_resources.resource_filename("cloudooo.handler.ooo",
                                          "/helper/unoconverter.py"),
          "--convert",
          "--uno_path=%s" % self.uno_path,
          "--office_binary_path=%s" % self.office_binary_path,
          "--hostname=%s" % self.hostname,
          "--port=%s" % self.port,
          "--document_url=%s" % self.document.getUrl(),
          "--destination_format=%s" % "doc",
          "--source_format=%s" % "odt",
          "--mimemapper=%s" % mimemapper_pickled]
    stdout, stderr = Popen(command,
                           stdout=PIPE,
                           stderr=PIPE).communicate()
    self.assertEquals(stderr, '')
    output_url = stdout.replace('\n', '')
    self.assertTrue(exists(output_url), stdout)
    mime = magic.Magic(mime=True)
    self.assertEquals(mime.from_file(output_url), 'application/msword')
    self.document.trash()
    self.assertEquals(exists(output_url), False)


