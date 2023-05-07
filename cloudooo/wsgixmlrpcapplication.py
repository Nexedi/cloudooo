#   Copyright (c) 2006-2007 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
from xmlrpc.server import SimpleXMLRPCDispatcher

logger = logging.getLogger(__name__)

class ErrorLoggingXMLRPCDispatcher(SimpleXMLRPCDispatcher):
    """A XMLRPC Dispatcher which logs errors
    """
    def _dispatch(self, method, params):
        try:
            return super()._dispatch(method, params)
        except:
            logger.exception("Error calling %s", method)
            raise


class WSGIXMLRPCApplication:
    """Application to handle requests to the XMLRPC service"""

    def __init__(self, instance=None, methods=[]):
        """Create windmill xmlrpc dispatcher"""
        self.dispatcher = ErrorLoggingXMLRPCDispatcher(
          allow_none=True,
          encoding=None)
        if instance is not None:
            self.dispatcher.register_instance(instance)
        for method in methods:
            self.dispatcher.register_function(method)
        self.dispatcher.register_introspection_functions()

    def handler(self, environ, start_response):
        """XMLRPC service for windmill browser core to communicate with"""
        if environ['REQUEST_METHOD'] == 'POST':
            return self.handle_POST(environ, start_response)
        else:
            start_response("400 Bad request", [('Content-Type', 'text/plain')])
            return [b'']

    def handle_POST(self, environ, start_response):
        """Handles the HTTP POST request.

        Attempts to interpret all HTTP POST requests as XML-RPC calls,
        which are forwarded to the server's _dispatch method for handling.

        Most code taken from SimpleXMLRPCServer with modifications for wsgi and
        my custom dispatcher.
        """
        try:
            # Get arguments by reading body of request.
            # We read this in chunks to avoid straining

            length = int(environ['CONTENT_LENGTH'])
            data = environ['wsgi.input'].read(length)

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and
            # using that method if present.
            response = self.dispatcher._marshaled_dispatch(
                    data, getattr(self.dispatcher, '_dispatch', None)
                )
            response += b'\n'
        except:  # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            logger.exception("Error serving request")
            start_response("500 Server error", [('Content-Type',
                                                 'text/plain')])
            return []
        else:
            # got a valid XML RPC response
            start_response("200 OK", [('Content-Type', 'text/xml'),
                                      ('Content-Length', str(len(response)),),
                                      ('Access-Control-Allow-Origin', '*')])
            return [response]

    def __call__(self, environ, start_response):
      return self.handler(environ, start_response)
