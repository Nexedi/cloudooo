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

from xmlrpclib import ServerProxy, Fault
from base64 import encodestring, decodestring
from cloudooo.handler.tests.handlerTestCase import HandlerTestCase, make_suite
import magic

file_detector = magic.Magic(mime=True)
DAEMON = True

class TestLegacyInterface(HandlerTestCase):

  def afterSetUp(self):
    """Create connection with cloudooo server"""
    self.proxy = ServerProxy("http://%s:%s/RPC2" % (self.hostname,
                                                    self.cloudooo_port),
                             allow_none=True)

  def testHtmlToBaseFormatConversion(self):
    """Check implicit base conversion of HTML documents.
    """
    filename = 'data/test_failure_conversion.html'
    file_object =  open(filename, 'r')
    original_data = file_object.read()
    file_object.close()
    status, response_dict, message = self.proxy.run_convert(
                                                  filename,
                                                  encodestring(original_data),
                                                  None,
                                                  None,
                                                  'text/html')
    converted_data = response_dict['data']
    mimetype = response_dict['mime']
    self.assertEquals(file_detector.from_buffer(decodestring(converted_data)),
                      'text/html')
    self.assertEquals(mimetype, 'text/html')

  def testHtmlToOdt(self):
    """Check conversion of HTML to odt
    """
    filename = 'data/test_failure_conversion.html'
    file_object =  open(filename, 'r')
    data = file_object.read()
    file_object.close()
    status, response_dict, message = self.proxy.run_generate(filename,
                                                             encodestring(data),
                                                             None,
                                                             'odt',
                                                             'text/html')
    data = response_dict['data']
    mimetype = response_dict['mime']
    self.assertEquals(file_detector.from_buffer(decodestring(data)),
                      'application/vnd.oasis.opendocument.text')
    self.assertEquals(mimetype, 'application/vnd.oasis.opendocument.text')

def test_suite():
  return make_suite(TestLegacyInterface)
