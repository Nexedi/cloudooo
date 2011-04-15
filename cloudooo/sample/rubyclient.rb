##############################################################################
#
# Copyright (c) 2009-2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Gabriel M. Monnerat <gabriel@tiolive.com>
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
