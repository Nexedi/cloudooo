##############################################################################
#
# Copyright (c) 2009-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Gabriel M. Monnerat <gabriel@tiolive.com>
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

require 'xmlrpc/client'

input_filename = File.dirname(__FILE__) + '/../handler/ooo/tests/data/test.doc'
output_filename = 'ruby_test.odt'

in_data = File.read input_filename
enc_data = XMLRPC::Base64.encode in_data

server = XMLRPC::Client.new2 'http://localhost:8008'
result = server.call('convertFile', enc_data, 'doc', 'odt')

out_data = XMLRPC::Base64.decode result
out_file = File.open(output_filename, 'w')
out_file.print out_data
out_file.close

data_length = out_data.length
if data_length == 8124 || data_length == 8101
  puts data_length
  puts "OK"
end
