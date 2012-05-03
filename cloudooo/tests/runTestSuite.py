
import cloudooo
from CloudoooTestSuite import CloudoooTestSuite 

import glob, sys, time, argparse, xmlrpclib, pprint, socket
import threading

class DummyTaskDistributionTool(object):

  def __init__(self):
    self.lock = threading.Lock()

  def createTestResult(self, name, revision, test_name_list, allow_restart,
      *args):
    self.test_name_list = list(test_name_list)
    return None, revision

  def updateTestResult(self, name, revision, test_name_list):
    self.test_name_list = list(test_name_list)
    return None, revision

  def startUnitTest(self, test_result_path, exclude_list=()):
    with self.lock:
      for i, test in enumerate(self.test_name_list):
        if test not in exclude_list:
          del self.test_name_list[i]
          return None, test

  def stopUnitTest(self, test_path, status_dict):
    pass

def safeRpcCall(function, *args):
  retry = 64
  xmlrpc_arg_list = []
  for argument in args:
    if isinstance(argument, dict):
      argument = dict([(x, isinstance(y,str) and xmlrpclib.Binary(y) or y) \
           for (x,y) in argument.iteritems()])
    xmlrpc_arg_list.append(argument)
  while True:
    try:
      return function(*xmlrpc_arg_list)
    except (socket.error, xmlrpclib.ProtocolError, xmlrpclib.Fault), e:
      print >>sys.stderr, e
      pprint.pprint(args, file(function._Method__name, 'w'))
      time.sleep(retry)
      retry += retry >> 1
 
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

  if args.master_url is not None:
    master_url = args.master_url
    if master_url[-1] != '/':
      master_url += '/'
    master = xmlrpclib.ServerProxy("%s%s" %
              (master_url, 'portal_task_distribution'),
              allow_none=1)
    assert master.getProtocolRevision() == 1
  else:
    master = DummyTaskDistributionTool()

  test_suite_title = args.test_suite_title or args.test_suite
  revision = args.revision
  suite = CloudoooTestSuite(1, test_suite=args.test_suite,
                            node_quantity=args.node_quantity,
                            revision=revision)

  test_result = safeRpcCall(master.createTestResult,
    args.test_suite, revision, suite.getTestList(),
    suite.allow_restart, test_suite_title, args.test_node_title,
    args.project_title)
  if test_result:
    test_result_path, test_revision = test_result
    while suite.acquire():
      test = safeRpcCall(master.startUnitTest, test_result_path,
                          suite.running.keys())
      if test:
        suite.start(test[1], lambda status_dict, __test_path=test[0]:
          safeRpcCall(master.stopUnitTest, __test_path, status_dict))
      elif not suite.running:
        break
