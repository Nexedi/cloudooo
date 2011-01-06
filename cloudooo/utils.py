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
from os import remove, environ
from shutil import rmtree
import logging

logger = logging.getLogger('Cloudooo')

PYTHON_ENVIRONMENT = [
      'PYTHONHOME',
      'PYTHONPATH',
      'PYTHONSTARTUP',
      'PYTHONY2K',
      'PYTHONOPTIMIZE',
      'PYTHONDEBUG',
      'PYTHONDONTWRITEBYTECODE',
      'PYTHONINSPECT',
      'PYTHONNOUSERSITE',
      'PYTHONNOUSERSITE',
      'PYTHONUNBUFFERED',
      'PYTHONVERBOSE'
]


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
    sleep(1)
    if daemon.status():
      return


def waitStopDaemon(daemon, attempts=5):
  """Wait a certain time to stop the daemon."""
  for num in range(attempts):
    sleep(1)
    if not daemon.status():
      break


def configureLogger(level=None, debug_mode=False):
  """Configure logger.
  Keyword arguments:
  level -- Level to prints the log messages
  """
  if level is None:
    level = logging.INFO

  if debug_mode:
    level = logging.DEBUG

  handler_list = logger.handlers
  if handler_list:
    for handler in iter(handler_list):
      logger.removeHandler(handler)
  # The propagate value indicates whether or not parents of this loggers will
  # be traversed when looking for handlers. It doesn't really make sense in the
  # root logger - it's just there because a root logger is almost like any
  # other logger.
  logger.propagate = 0
  logger.setLevel(level)
  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(level)
  # create formatter
  formatter = logging.Formatter("%(asctime).19s - %(name)s - %(levelname)s - %(message)s")
  # add formatter to ch
  ch.setFormatter(formatter)
  # add ch to logger
  logger.addHandler(ch)


def remove_file(filepath):
  try:
    remove(filepath)
  except OSError, msg:
    print msg.strerror


def convertStringToBool(string):
  """This function is used to convert string 'true' and 'false' only.
  Keyword arguments:
  string -- string to convert to boolean
  """
  if string.upper() == "TRUE":
    return True
  elif string.upper() == "FALSE":
    return False
  else:
    return None
