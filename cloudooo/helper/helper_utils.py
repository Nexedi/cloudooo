def getServiceManager(host, port):
  """Get the ServiceManager from the running OpenOffice.org."""
  import uno
  # Get the uno component context from the PyUNO runtime
  uno_context = uno.getComponentContext()
  # Create the UnoUrlResolver on the Python side.
  url_resolver = "com.sun.star.bridge.UnoUrlResolver"
  resolver = uno_context.ServiceManager.createInstanceWithContext(url_resolver,
    uno_context)
  # Connect to the running OpenOffice.org and get its
  # context.
  uno_connection = resolver.resolve("uno:socket,host=%s,port=%s;urp;StarOffice.ComponentContext" % (host, port))
  # Get the ServiceManager object
  return uno_connection.ServiceManager
