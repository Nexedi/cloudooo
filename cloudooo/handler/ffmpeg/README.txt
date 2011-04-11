FFMPEG Handler http://svn.erp5.org/erp5/trunk/utils/cloudooo.handler.ffmpeg/

There are three binaries available:

 - ffmpeg
 - ffprobe
 - ffserver

First is used to convert audio and video file to availables codecs into cloudooo
at the moment( for seeing then use -codecs option).
Second one is used for seeing file information, like metadata in this.
Third is only used in case to overwrite ffmpeg server.

Runnig any of those binaries with -h or --help option will more command line
help and options.

Usage Example
-------------

Converting ogv file into mpeg file format:

 $ ffmpeg -i test.ogv test.mpeg

Getting file information:

 $ ffprobe test.ogv

Inserting metadata into file:
 $ ffmpeg -i test.ogv -metadata string=string -metadata string=string test.mepg

Converting its necessary for insert metadata, but changing format is not.
