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

import os
from time import sleep
from os import remove
from shutil import rmtree
from cloudooo.util import logger
from psutil import process_iter, Process, NoSuchProcess, wait_procs
import signal


def removeDirectory(path):
  """Remove directory"""
  try:
    rmtree(path)
  except OSError, msg:
    logger.error(msg)

def waitStartDaemon(daemon, attempts):
  """Wait a certain time to start the daemon."""
  for num in range(attempts):
    if not daemon.isRunning():
      return False
    elif daemon.status():
      return True
    sleep(1)
  return False


def waitStopDaemon(daemon, attempts=5):
  """Wait a certain time to stop the daemon."""
  for num in range(attempts):
    if not daemon.status():
      return True
    sleep(1)
  return False

def processUsedFilesInPath(path):
  pids = set()
  for p in process_iter(attrs=['open_files', 'memory_maps']):
    for f in (p.info['open_files'] or []) + (p.info['memory_maps'] or []):
      if f.path.startswith(path):
        pids.add(p.pid)
  return pids

def kill_procs_tree(pids, sig=signal.SIGTERM,
                   timeout=3, on_terminate=None):
  pids = set(pids)
  children_pids = set(pids)
  for pid in pids:
    parent = None
    try:
      parent = Process(pid)
    except NoSuchProcess:
      pass
    if parent:
      children = parent.children(recursive=True)
      for p in children:
        children_pids.add(p.pid)
  my_pid = os.getpid()
  if my_pid in children_pids:
    children_pids.remove(my_pid)
  pids = []
  for pid in children_pids:
    try:
      p = Process(pid)
      p.send_signal(sig)
      pids.append(p)
    except NoSuchProcess:
      pass
  gone, alive = wait_procs(pids, timeout=timeout,
                                  callback=on_terminate)
  return (gone, alive)

def remove_file(filepath):
  try:
    remove(filepath)
  except OSError, msg:
    print msg.strerror
