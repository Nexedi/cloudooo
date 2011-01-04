from request import MonitorRequest
from memory import MonitorMemory
from sleeping_time import MonitorSpleepingTime
from cloudooo.handler.ooo.application.openoffice import openoffice

monitor_request = None
monitor_memory = None
monitor_sleeping_time = None

def load(local_config):
  """Start the monitors"""
  monitor_interval = int(local_config.get('monitor_interval'))
  global monitor_request
  monitor_request = MonitorRequest(openoffice,
                              monitor_interval,
                              int(local_config.get('limit_number_request')))
  monitor_request.start()

  if bool(local_config.get('enable_memory_monitor')):
    global monitor_memory
    monitor_memory = MonitorMemory(openoffice,
                                  monitor_interval,
                                  int(local_config.get('limit_memory_used')))
    monitor_memory.start()
  time_before_sleep = int(local_config.get('max_sleeping_duration', 0))
  if time_before_sleep:
    global monitor_sleeping_time
    monitor_sleeping_time = MonitorSpleepingTime(openoffice,
                                                 monitor_interval,
                                                 time_before_sleep)
    monitor_sleeping_time.start()
  return


def stop():
  """Stop all monitors"""
  if monitor_request:
    monitor_request.terminate()
  if monitor_memory:
    monitor_memory.terminate()
  if monitor_sleeping_time is not None:
    monitor_sleeping_time.terminate()
  clear()


def clear():
  global monitor_request, monitor_memory, monitor_sleeping_time
  monitor_request = None
  monitor_memory = None
  monitor_sleeping_time = None
