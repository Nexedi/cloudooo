##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
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

"""Start cloudooo with Waitress.

Usage:

  cloudooo-server serve [--log-file LOG_FILE] CONFIG_FILE
"""

import argparse
import configparser
import logging
from os import path


def main(argv=None):
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('command', choices=('serve',))
  parser.add_argument('--log-file', help='append logs to this file')
  parser.add_argument('config_file', help='PasteDeploy configuration file')
  namespace = parser.parse_args(argv)

  if namespace.log_file:
    logging.basicConfig(
      filename=namespace.log_file, filemode='a', level=logging.INFO,
      format='%(message)s')

  from paste.deploy import loadapp
  from paste.translogger import TransLogger
  from waitress import serve

  config_path = path.abspath(namespace.config_file)
  app = loadapp('config:' + config_path)

  config = configparser.RawConfigParser()
  with open(config_path) as config_file:
    config.read_file(config_file)
  host = config.get('server:main', 'host', fallback='127.0.0.1')
  port = config.getint('server:main', 'port', fallback=8000)
  threads = config.getint('server:main', 'threads', fallback=10)

  serve(
    TransLogger(app, setup_console_handler=not namespace.log_file),
    host=host, port=port, threads=threads)
