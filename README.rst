Install Cloudooo
================

::
  
  $ python2.6 setup.py install


Warnings:
 - you must have installed setuptools>=0.6c11 in this python.

Install LibreOffice / OpenOffice.org
====================================

Install LibreOffice or OpenOffice.org.
  - http://www.libreoffice.org/download/
  - http://download.openoffice.org/

Create Configuration File
=========================

The configuration file is used to start the application using paster.

::
  
  $ cp ./cloudooo/sample/sample.conf . # Copy to current folder

The next step is define some attributes in cloudooo.conf:
    - working_path - folder to run the application. This folder need be created.
    - uno_path - folder where UNO library is installed (ex. /opt/libreoffice/basis-link/program/)
    - soffice_binary_path - folder where soffice.bin is installed (ex. /opt/libreoffice/program/)

Run Application
===============

::
  
  $ paster serve ./cloudooo.conf


or run as a daemon:

::
  
  $ paster serve ./cloudoo.conf --daemon


Stop Application
================

::
  
  $ kill -1 PASTER_PID

Warning: always use SIGHUP because only with this signal all processes are stopped correctly.

Cloudooo Description
====================

- XMLRPC + WSGI will be one bridge for easy access to LibreOffice / OpenOffice.org. This will implement one XMLRPC server into WSGI (Paster).
- PyUno is used to connect to LibreOffice / OpenOffice.org stated with open socket. The features will be handled all by pyuno.
- Only a process will have access to LibreOffice / OpenOffice.org by time.
- All clients receive the same object(proxy) when connects with XMLRPC Server.


Managing LibreOffice / OpenOffice.org process


- start 'soffice.bin':
  
  - Pyuno start 'soffice.bin' processes and the communication is through sockets
  
  - 'soffice.bin' processes run in brackground;

- control 'soffice.bin':
     
  - If the socket lose the connection, cloudooo kills the process, restarts processes and submit again the file;


XMLRPC Server - XMLRPC + WSGI
-----------------------------

- Send document to 'soffice.bin' and return the document converted with metadata
  - XMLRPC receives a file and connects to 'soffice.bin' process by pyuno;
  - The pyuno opens a new document, write, add metadata and returns the document edited or converted to xmlrpc and it return the document to the user;
  - When finalize the use of 'soffice.bin', should make sure that it was finalized;
- Export to another format;
- Invite document and return metadata only;
- Edit metadata of the document;
- Problems and possible solutions
  
  - 'soffice.bin' is stalled;
  
    - finalize the process, start 'soffice.bin' and submit the document again (without restart the cloudooo);
  
  - 'soffice.bin' is crashed;
    
    - finalize the process, verify if all the process was killed, start 'soffice.bin' and submit the document again(without restart the cloudooo)
    
  - 'soffice.bin' received the document and stalled;
    
    - if 'soffice.bin' isn't responding, kill the process and start
     
  - The document that was sent is corrupted;
    
    - write in log the error and verify that the process aren't in memory


FFMPEGHandler
====================

FFMPEGHandler is a handler of cloudooo for developing GUI convertion applications
using FFmpeg cross-platform.

Introduction
The FFMPEGHandler package defines a single class, Handler, which is interface to
audio and video convertion into cloudooo.

FFMPEGHandler has been developed with python 2.6 and ffmpeg 0.6.1.

Example

Converting file:

>>> from cloudooo.handler.ffmpeg import Handler
>>> handler = Handler('my_path_data', open(test.ogv).read(), 'ogv')
>>> converted_data = handler.convert('mpeg')

Getting information of file:

>>> from cloudooo.handler.ffmpeg import Handler
>>> handler = Handler('my_path_data', open(test.ogv).read(), 'ogv')
>>> metadata = handler.getMetadata()
>>> metadata
{ 'ENCODER': 'Lavf52.64.2'}

NOTE

In case of importing FFMPEGHandler library is needed to import its used libraries
as well and set its enviroment for handler.

Example

>>> from cloudooo.handler.ffmpeg import Handler
>>> self.kw = dict(env=dict(PATH="../software/parts/ffmpeg/bin"))
>>> handler = Handler('my_path_data', open(test.ogv).read(), 'ogv', **self.kw)
>>> converted_data = handler.convert('mpeg')

