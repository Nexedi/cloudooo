#!/usr/bin/env python

import sys
import unittest
from argparse import ArgumentParser
from time import sleep
from cloudooo.handler.ooo.utils.utils import socketStatus
from ConfigParser import ConfigParser
from os import chdir, path, environ, curdir
from subprocess import Popen

ENVIRONMENT_PATH = path.abspath(path.dirname(__file__))

#XXX nicolas: I don not know if still useful
# since optparse replaced getopt
__doc__ = """Unit Test Runner for Cloudooo
usage: %(program)s [options] Unit_Test_Name

Options:
  -h, --help                         Display help documentation
  --server_cloudooo_conf=STRING      Path to cloudooo configuration file
  --paster_path=STRING               Path to Paster script
  --with-daemon                      it starts the cloudooo daemon
  --with-openoffice                  it starts one Xvfb and one OpenOffice.org
  --with-xvfb                        it starts one Xvfb only
"""


def wait_liberate_port(hostname, port, timeout_limit=30):
  for n in range(timeout_limit):
    if not socketStatus(hostname, port):
      break
    sleep(1)


def wait_use_port(hostname, port, timeout_limit=30):
  for n in range(timeout_limit):
    if socketStatus(hostname, port):
      break
    sleep(1)


def exit(msg):
  sys.stderr.write(msg)
  sys.exit(0) 


def run_test(test_name):
  module = __import__(test_name)
  if not hasattr(module, "test_suite"):
    exit("No test suite to run, exiting immediately")
  TestRunner = unittest.TextTestRunner
  suite = unittest.TestSuite()
  suite.addTest(module.test_suite())
  TestRunner(verbosity=2).run(suite)


def run():
  parser = ArgumentParser()
  parser.add_argument('server_cloudooo_conf')
  parser.add_argument('test_name')
  parser.add_argument('--with-daemon', dest='DAEMON',
                      action='store_true')
  parser.add_argument('--with-openoffice', dest='OPENOFFICE',
                      action='store_true')
  parser.add_argument('--with-xvfb', dest='XVFB',
                      action='store_true')
  parser.add_argument('--timeout_limit', dest='timeout_limit',
                      type=long, default=30)
  parser.add_argument('--paster_path', dest='paster_path',
                      default='paster')
  namespace = parser.parse_args()

  server_cloudooo_conf = namespace.server_cloudooo_conf
  test_name = namespace.test_name
  if server_cloudooo_conf.startswith(curdir):
    server_cloudooo_conf = path.join(path.abspath(curdir),
                                     server_cloudooo_conf)

  DAEMON = namespace.DAEMON
  OPENOFFICE = namespace.OPENOFFICE
  XVFB = namespace.XVFB
  paster_path = namespace.paster_path

  python_extension = '.py'
  if test_name[-3:] == python_extension:
    test_name = test_name[:-3]
  if not path.exists(path.join(ENVIRONMENT_PATH, 
                               '%s%s' % (test_name, python_extension))):
    exit("%s not exists\n" % test_name)

  from cloudoooTestCase import loadConfig, startFakeEnvironment, stopFakeEnvironment

  sys.path.append(ENVIRONMENT_PATH)

  config = ConfigParser()
  config.read(server_cloudooo_conf)
  openoffice_port = int(config.get("app:main", "openoffice_port"))
  xvfb_port = int(config.get("app:main", "virtual_display_port"))
  xvfb_display_id = int(config.get("app:main", "virtual_display_id"))
  hostname = config.get("app:main", "application_hostname")
  server_port = int(config.get("server:main", "port"))
  run_dir = config.get('app:main', 'working_path')
  if DAEMON:
    loadConfig(server_cloudooo_conf)
    command = [paster_path, "serve", server_cloudooo_conf]
    process = Popen(command)
    wait_use_port(hostname, openoffice_port)
    wait_use_port(hostname, server_port)
    chdir(ENVIRONMENT_PATH)
    try:
      run_test(test_name)
    finally:
      process.send_signal(1)
      wait_liberate_port(hostname, server_port)
      process.terminate()
    wait_liberate_port(hostname, server_port)
  elif OPENOFFICE:
    chdir(ENVIRONMENT_PATH)
    openoffice, xvfb = startFakeEnvironment(conf_path=server_cloudooo_conf)
    run_test(test_name)
    stopFakeEnvironment()
  elif XVFB:
    chdir(ENVIRONMENT_PATH)
    xvfb = startFakeEnvironment(start_openoffice=False,
                                conf_path=server_cloudooo_conf)
    run_test(test_name)
    stopFakeEnvironment(stop_openoffice=False)
  else:
    chdir(ENVIRONMENT_PATH)
    loadConfig(server_cloudooo_conf)
    run_test(test_name)

if __name__ == "__main__":
  run()
