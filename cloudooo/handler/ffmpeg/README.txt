FFMPEGHandler
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

