##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat  <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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

import cloudooo
import argparse
import sys
import glob
import os
import shlex
from erp5.util.testsuite import TestSuite as BaseTestSuite
from erp5.util.testsuite import SubprocessError
from erp5.util import taskdistribution

def _parsingErrorHandler(data, _):
  print >> sys.stderr, 'Error parsing data:', repr(data)
taskdistribution.patchRPCParser(_parsingErrorHandler)

class TestSuite(BaseTestSuite):

  def run(self, test):
    return self.runUnitTest(test)

  def runUnitTest(self, *args, **kw):
    try:
      runUnitTest = os.environ.get('RUN_UNIT_TEST',
                                   'runUnitTest')
      args = tuple(shlex.split(runUnitTest)) + args
      status_dict = self.spawn(*args, **kw)
    except SubprocessError as e:
      status_dict = e.status_dict
    test_log = status_dict['stderr']
    search = self.RUN_RE.search(test_log)
    if search:
      groupdict = search.groupdict()
      status_dict.update(duration=float(groupdict['seconds']),
                         test_count=int(groupdict['all_tests']))
    search = self.STATUS_RE.search(test_log)
    if search:
      groupdict = search.groupdict()
      status_dict.update(
        error_count=int(groupdict['errors'] or 0),
        failure_count=int(groupdict['failures'] or 0)
                     +int(groupdict['unexpected_successes'] or 0),
        skip_count=int(groupdict['skips'] or 0)
                  +int(groupdict['expected_failures'] or 0))
    return status_dict

  def getTestList(self):
    test_list = []
    for test_path in glob.glob('/%s/handler/*/tests/test*.py' %
                                  "/".join(cloudooo.__file__.split('/')[:-1])):
      test_case = test_path.split(os.sep)[-1][:-3] # remove .py
      # testOooMonitorRequest is making testsuite stall.
      if test_case not in ['testOooHighLoad', 'testOooMonitorRequest'] and \
         not test_case.startswith("testFfmpeg"):
        test_list.append(test_case)
    return test_list

def run():
  parser = argparse.ArgumentParser(description='Run a test suite.')
  parser.add_argument('--test_suite', help='The test suite name')
  parser.add_argument('--test_suite_title', help='The test suite title',
                      default=None)
  parser.add_argument('--test_node_title', help='The test node title',
                      default=None)
  parser.add_argument('--project_title', help='The project title',
                      default=None)
  parser.add_argument('--revision', help='The revision to test',
                      default='dummy_revision')
  parser.add_argument('--node_quantity', help='Number of parallel tests to run',
                      default=1, type=int)
  parser.add_argument('--master_url',
                      help='The Url of Master controling many suites',
                      default=None)


  args = parser.parse_args()
  master = taskdistribution.TaskDistributor(args.master_url)
  test_suite_title = args.test_suite_title or args.test_suite
  revision = args.revision
  suite = TestSuite(1, test_suite=args.test_suite,
                    node_quantity=args.node_quantity,
                    revision=revision)

  test_result = master.createTestResult(revision, suite.getTestList(),
    args.test_node_title, suite.allow_restart, test_suite_title,
    args.project_title)
  if test_result is not None:
    assert revision == test_result.revision, (revision, test_result.revision)
    while suite.acquire():
      test = test_result.start(suite.running.keys())
      if test is not None:
        suite.start(test.name, lambda status_dict, __test=test:
          __test.stop(**status_dict))
      elif not suite.running:
        break
