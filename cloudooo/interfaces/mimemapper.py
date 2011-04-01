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

from zope.interface import Interface


class IMimemapper(Interface):
  """Provide methods to manipulate conversion abilities of
  handlers
  """

  def isLoaded():
    """Returns if mimemapper is bootstraped
    """

  def loadMimemapper():
    """bootstrap mimemapper of handler
    """

  def getAllowedExtensionInfoList(mimetype):
    """Return a detailed list of output mimetypes with a list of
    accepted parameter to perform the conversion:
      application/pdf: [('text/plain', ()),
                        ('image/png', ('frame', 'resolution', 'width', 'height',
                        'colorspace',)),
                        ...
                       ]
    """
