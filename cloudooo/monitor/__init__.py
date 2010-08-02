from request import MonitorRequest
from memory import MonitorMemory
from cloudooo.application.openoffice import openoffice

monitor_request = None
monitor_memory = None

def load(local_config):
  """Start the monitors"""
  global monitor_request
  monitor_request = MonitorRequest(openoffice,
                              int(local_config.get('monitor_interval')),
                              int(local_config.get('limit_number_request')))
  monitor_request.start()
  
  if bool(local_config.get('enable_memory_monitor')):
    global monitor_memory
    monitor_memory = MonitorMemory(openoffice,
                                  int(local_config.get('monitor_interval')),
                                  int(local_config.get('limit_memory_used')))
    monitor_memory.start()
  
  return

def stop():
  """Stop all monitors"""
  if monitor_request:
    monitor_request.terminate()
  if monitor_memory: 
    monitor_memory.terminate()
  clear()

def clear():
  global monitor_request, monitor_memory
  monitor_request = None
  monitor_memory = None
