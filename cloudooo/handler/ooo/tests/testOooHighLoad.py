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

from base64 import encodestring, decodestring
from multiprocessing import Process, Array
from cloudooo.tests.cloudoooTestCase import TestCase, make_suite
import magic

mime_decoder = magic.Magic(mime=True)


def basicTestToGenerate(id, proxy, data, source_format, destination_format,
                        result_list):
  """Test to use method generate of server"""
  document = proxy.convertFile(encodestring(data), source_format, destination_format)
  mimetype = mime_decoder.from_buffer(decodestring(document))
  assert mimetype == 'application/pdf'
  result_list[id] = True


class TestHighLoad(TestCase):
  """Test with many simultaneous connection"""

  def testGenerateHighLoad(self):
    """Sends many request to Server. Calling generate method"""
    process_list = []
    data = open("data/test.doc", 'r').read()
    LOOP = 100
    result_list = Array('i', [False] * LOOP)
    for id in range(LOOP):
      process = Process(target=basicTestToGenerate, args=(id, self.proxy, data,
                                                          'doc', 'pdf',
                                                          result_list))
      process.start()
      process_list.append(process)

    for proc in process_list[:]:
      proc.join()
      del proc
    self.assertTrue(all(result_list))


