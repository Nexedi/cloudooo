#!/usr/bin/env python

import sys
import unittest
from argparse import ArgumentParser
from os import path, curdir, environ, chdir

ENVIRONMENT_PATH = path.abspath(path.dirname(__file__))


def exit(msg):
  sys.stderr.write(msg)
  sys.exit(0)


# XXX - Duplicated function. This function must be generic to be used by all handlers
def run():
  parser = ArgumentParser(description="Unit Test Runner for Cloudooo")
  parser.add_argument('server_cloudooo_conf')
  parser.add_argument('test_name')
  parser.add_argument('--paster_path', dest='paster_path',
                      default='paster',
                      help="Path to Paster script")
  namespace = parser.parse_args()

  server_cloudooo_conf = namespace.server_cloudooo_conf
  test_name = namespace.test_name
  if server_cloudooo_conf.startswith(curdir):
    server_cloudooo_conf = path.join(path.abspath(curdir),
                                     server_cloudooo_conf)
  environ['server_cloudooo_conf'] = server_cloudooo_conf

  python_extension = '.py'
  if test_name[-3:] == python_extension:
    test_name = test_name[:-3]
  if not path.exists(path.join(ENVIRONMENT_PATH,
                               '%s%s' % (test_name, python_extension))):
    exit("%s not exists\n" % test_name)

  sys.path.append(ENVIRONMENT_PATH)

  module = __import__(test_name)
  if not hasattr(module, "test_suite"):
    exit("No test suite to run, exiting immediately")

  TestRunner = unittest.TextTestRunner
  suite = unittest.TestSuite()
  suite.addTest(module.test_suite())
  chdir(ENVIRONMENT_PATH)
  TestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
  run()
