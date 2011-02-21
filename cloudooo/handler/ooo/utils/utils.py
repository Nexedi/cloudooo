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

from socket import socket, error
from errno import EADDRINUSE
from time import sleep
from os import remove
from shutil import rmtree
from cloudooo.utils.utils import logger


def removeDirectory(path):
  """Remove directory"""
  try:
    rmtree(path)
  except OSError, msg:
    logger.error(msg)


def socketStatus(hostname, port):
  """Verify if the address is busy."""
  try:
    socket().bind((hostname, port),)
    # False if the is free
    return False
  except error, (num, err):
    if num == EADDRINUSE:
      # True if the isn't free
      return True


def waitStartDaemon(daemon, attempts):
  """Wait a certain time to start the daemon."""
  for num in range(attempts):
    if daemon.status():
      return True
    elif daemon.pid() is None:
      return False
    sleep(1)
  return False


def waitStopDaemon(daemon, attempts=5):
  """Wait a certain time to stop the daemon."""
  for num in range(attempts):
    if not daemon.status():
      return True
    sleep(1)
  return False


def remove_file(filepath):
  try:
    remove(filepath)
  except OSError, msg:
    print msg.strerror
