#!/usr/bin/env python

import sys
from pkg_resources import resource_filename
import logging
import unittest
from time import sleep
from subprocess import Popen
from ConfigParser import ConfigParser
from argparse import ArgumentParser
from os import chdir, path, environ, curdir, remove
from glob import glob
import psutil
from signal import SIGQUIT


def wait_use_port(pid, timeout_limit=30):
  process = psutil.Process(pid)
  for n in range(timeout_limit):
    if len(process.connections()) > 0:
      return True
    sleep(1)
  return False


logger = logging.getLogger(__name__)

def run():
  description = "Unit Test Runner for Handlers"
  parser = ArgumentParser(description=description)
  parser.add_argument('server_cloudooo_conf')
  parser.add_argument('test_name')
  parser.add_argument('--timeout_limit', dest='timeout_limit',
                      type=int, default=30,
                      help="Timeout to waiting for the cloudooo stop")
  parser.add_argument('--paster_path', dest='paster_path',
                      default='paster',
                      help="Path to Paster script")
  parser.add_argument('-v', '--verbose', action='store_true', help='Enable logging')
  parser.add_argument(
    '-D', '--debug', action='store_true',
    help='Enable pdb on errors/failures') # XXX but does not show test output
  namespace = parser.parse_args()
  if namespace.verbose:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',)
  environment_path = glob(path.join(resource_filename("cloudooo", "handler"), '*', 'tests'))
  sys.path.extend(environment_path)
  server_cloudooo_conf = namespace.server_cloudooo_conf
  test_name = namespace.test_name
  if server_cloudooo_conf.startswith(curdir):
    server_cloudooo_conf = path.join(path.abspath(curdir),
                                     server_cloudooo_conf)
  environ['server_cloudooo_conf'] = server_cloudooo_conf
  paster_path = namespace.paster_path

  from cloudooo.tests.handlerTestCase import startFakeEnvironment
  from cloudooo.tests.handlerTestCase import stopFakeEnvironment

  config = ConfigParser()
  config.read(server_cloudooo_conf)

  if namespace.debug:
    # XXX not really correct but enough to get a pdb prompt
    suite = unittest.defaultTestLoader.loadTestsFromName(test_name)
    module = __import__(list(suite)[0].__module__)
    if module is unittest:
      module = __import__(list(list(suite)[0])[0].__module__)
  else:
    module = __import__(test_name)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)

  handler_path = path.dirname(module.__file__)
  DAEMON = getattr(module, 'DAEMON', False)
  OPENOFFICE = getattr(module, 'OPENOFFICE', False)

  def run_suite():
    if namespace.debug:
      import functools
      suite.run = functools.partial(suite.run, debug=True)
    try:
      unittest.TextTestRunner(
        verbosity=2,
        warnings=None if sys.warnoptions else 'default',
      ).run(suite)
    except:
      import pdb; pdb.post_mortem()
      raise

  if DAEMON:
    log_file = '%s/cloudooo_test.log' % config.get('app:main',
                                                   'working_path')
    if path.exists(log_file):
      remove(log_file)
    command = [paster_path, 'serve', '--log-file', log_file,
               server_cloudooo_conf]
    process = Popen(command)
    logger.debug("Started daemon %s", command)
    wait_use_port(process.pid)
    logger.debug("Daemon ready")
    chdir(handler_path)
    try:
      run_suite()
    finally:
      process.send_signal(SIGQUIT)
      process.wait()
  elif OPENOFFICE:
    chdir(handler_path)
    logger.debug("Starting fake environment")
    startFakeEnvironment(conf_path=server_cloudooo_conf)
    logger.debug("Fake environment ready")
    try:
      run_suite()
    finally:
      stopFakeEnvironment()
  else:
    chdir(handler_path)
    run_suite()
