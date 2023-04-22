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

import sys
from multiprocessing import Process
from os import listdir
from xmlrpc.client import ServerProxy
from os.path import join
from getopt import getopt, GetoptError
from time import ctime, time
from base64 import encodebytes

__doc__ = """
usage: python HighTestLoad.py [options]

Options:
  -h, --help        this help screen

  -f  folder        Full url of folder with documents
  -c  concurrency   Number of clients
  -n  requests      Number of requests
  -s  server        Server Address e.g http://ip:port/
  -l  filter log    Folder to store logs
"""


class Log:
  """Object to manipulate the log file"""

  def __init__(self, log_path, mode='a'):
    """Open the log file in filesystem"""
    self._log = open(log_path, mode)

  def msg(self, message):
    """Write the message in file"""
    self._log.write(message)

  def close(self):
    """Close the file"""
    self._log.close()

  def flush(self):
    """Flush the internal I/O buffer."""
    self._log.flush()


class Client(Process):
  """Represents a client that sends requests to the server. The log file by
  default is created in current path, but can be created in another path.

  In log are stored:
  - Date and time that the client initiated the test;
  - Duration of each request;
  - Total time of all requets;
  - Data and time that the client finished the test;
  """

  def __init__(self, address, number_request, folder, **kw):
    """Client constructor

    address -- Complete address as string
      e.g http://localhost:8008
    number_request -- number of request that client will send to the server
    folder -- Full path to folder.
      e.g '/home/user/documents'
    """
    Process.__init__(self)
    self.address = address
    self.number_of_request = number_request
    self.folder = folder
    log_filename = kw['log_filename'] or "%s.log" % self.name
    log_folder_path = kw.get("log_folder_url", '')
    log_path = join(log_folder_path, log_filename)
    self.log = Log(log_path, 'w')

  def run(self):
    """ """
    time_list = []
    self.log.msg("Test Start: %s\n" % ctime())
    proxy = ServerProxy(self.address)
    while self.number_of_request:
      folder_list = listdir(self.folder)[:self.number_of_request]
      for filename in folder_list:
        file_path = join(self.folder, filename)
        data = encodebytes(open(file_path).read())
        self.log.msg("Input: %s\n" % file_path)
        try:
          now = time()
          proxy.convertFile(data, 'odt', 'doc')
          response_duration = time() - now
          self.log.msg("Duration: %s\n" % response_duration)
          time_list.append(response_duration)
          self.log.flush()
        except Exception as err:
          self.log.msg("%s\n" % str(err))
        self.number_of_request -= 1

    self.log.msg("Test Stop: %s\n" % ctime())
    self.log.msg("Total Duration: %s" % sum(time_list))
    self.log.close()


def main():

  help_msg = "\nUse --help or -h"
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "hc:n:f:s:l:", ["help"])
  except GetoptError as msg:
    msg = msg.msg + help_msg
    print(msg, file=sys.stderr)
    sys.exit(2)

  kw = {}
  for opt, arg in opt_list:
    if opt in ('-h', '--help'):
      print(__doc__, file=sys.stdout)
      sys.exit(2)
    elif opt == '-c':
      number_client = int(arg)
    elif opt == '-n':
      number_request = int(arg)
    elif opt == '-f':
      document_folder = arg
    elif opt == '-s':
      server_address = arg
    elif opt == '-l':
      kw['log_folder_url'] = arg

  client_list = []
  for num in range(number_client):
    kw['log_filename'] = "client%s.log" % num
    client = Client(server_address, number_request, document_folder, **kw)
    client_list.append(client)
    client.start()

  for client in client_list:
    client.join()

if __name__ == "__main__":
  main()
