Building Python GStreamer Pipelines
===================================

GStreamer and GObject can be used from Python via the python-gi and python-gst
modules. This repository is just a trivial docker file that gets you a working
gstreamer pipeline from which you can start building and exploring.

It is assumed that you understand how to program in Python. You can see the 
gstreamer script in `python/demo.py`.

Installation/prerequisites::

    $ apt-get install docker 
    $ pip3.5 install --user -I docker-compose

Running the demo::

    $ docker-compose up

Once the image comes up you'll see the following being logged::

    INFO:gstreamer-demo:message: <flags GST_MESSAGE_STATE_CHANGED of type Gst.MessageType>

which indicates that the gstreamer pipeline is producing HLS content.
You can now view the video by starting another window and running::

    $ vlc http://localhost:8080/index.m3u8

and you should see the video-test-pattern displayed in VLC.
