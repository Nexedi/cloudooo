##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Gabriel M. Monnerat <gmonnerat@iff.edu.br>
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

from subprocess import Popen, PIPE
from cloudooo.utils import logger, waitStartDaemon, remove_file
from zope.interface import implements
from application import Application
from cloudooo.interfaces.application import IApplication
from os.path import exists

class Xvfb(Application):
  """Start and control Xvfb. It is used to open/run
  instances OpenOffice.
  """
  implements(IApplication)

  name = "xvfb"

  def loadSettings(self, hostname, port, path_run_dir, display_id, **kwargs):
    """Method to load the configuration to run and monitoring the Xvfb.

    Keyword Arguments:
    virtual_screen -- the display number
    """
    Application.loadSettings(self, hostname, port, path_run_dir, display_id)
    self.virtual_screen = kwargs.get('virtual_screen', '0')
    self.process_name = "Xvfb"
    
  def start(self):
    """Method to start Virtual Frame Buffer."""
    self.command = ["Xvfb", "-ac", ":%s" % self.display_id, \
        "-screen", self.virtual_screen, "800x600x16", \
        "-fbdir", self.path_run_dir]
    self.process = Popen(self.command,
                        stdout=PIPE,
                        close_fds=True)
    waitStartDaemon(self, self.timeout)
    Application.start(self)
    logger.debug("Xvfb pid - %s" % self.pid())

  def stop(self):
    """Stop Xvfb processes and remove lock file in file system"""
    Application.stop(self)
    lock_filepath = '/tmp/.X%s-lock' % self.display_id
    if exists(lock_filepath):
      remove_file(lock_filepath)

    display_filepath = '/tmp/X11/X%s' % self.display_id
    if exists(display_filepath):
      remove_file(display_filepath)


xvfb = Xvfb()
