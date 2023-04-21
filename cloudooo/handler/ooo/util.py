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

from socket import socket, error
from errno import EADDRINUSE
from time import sleep
from os import remove
from shutil import rmtree
from cloudooo.util import logger


def removeDirectory(path):
  """Remove directory"""
  try:
    rmtree(path)
  except OSError as msg:
    logger.error(msg)


def socketStatus(hostname, port):
  """Verify if the address is busy."""
  try:
    socket().bind((hostname, port),)
    # False if the is free
    return False
  except error as err:
    if err.errno == EADDRINUSE:
      # True if the isn't free
      return True


def waitStartDaemon(daemon, attempts):
  """Wait a certain time to start the daemon."""
  for num in range(attempts):
    if daemon.status():
      return True
    elif daemon.hasExited():
      return False
    sleep(1)
  return False


def waitStopDaemon(daemon, attempts=5):
  """Wait a certain time to stop the daemon."""
  for num in range(attempts):
    if not daemon.status() or daemon.hasExited():
      return True
    sleep(1)
  return False


def remove_file(filepath):
  try:
    remove(filepath)
  except OSError as msg:
    print(msg.strerror)
