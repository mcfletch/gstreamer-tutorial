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

What's Going On?
----------------

The docker-ish parts are:

* there's an nginx server that's just doing static file serving (port 8080)
* there's an ubuntu yakkety image with gstreamer, python3-gst, and python3-gi
* there's a very small Python file (`python/demo.py`) that runs the pipeline

What's a Pipeline?
------------------

GStreamer is a pipeline-oriented media processing system. It works by hooking
up "pads" (sources, sinks) on elements and then allowing the low-level framework
to do the actual media processing.

The pipeline we're setting up is a trivial HTTP Live Streaming stream. It doesn't
do multiple encodes or anything fun like that. It just creates a single playlist
that includes:

* h264 video encoding
* aac audio encoding
* mpeg TS muxing and HLS playlist creation

and makes that available in the nginx server's root directory.

We're using the same command-line syntax to setup the pipeline as the 
gstreamer-tools `gst-launch` program uses. In this syntax you'll see 
elements (and caps) joined with `!` characters which act as a media 
pipe between the elements.

.. note::
    You can also setup the pipelines programatically by adding 
    individual elements to a pipeline instance.

You'll note that elements start with an element name:

* videotestsrc
* x264enc
* mpegtsmux
* hlssink
* audiotestsrc
* avenc_aac

and that they can have properties specified with x=y syntax:

* pattern=0
* bitrate=256
* name=muxer

The name property is special in that all elements have names, and 
you can use the name to get a handle to a property from your pipeline 
if you want to programatically manipulate the element.

You'll note that at the end of the audio pipeline we include:
`muxer.` which is actually saying "route this into the element 
named `muxer`.

Lastly, you'll note that we have two sections that look like:

* video/x-raw,framerate=30000/1001,width=720,height=480
* audio/x-raw,rate=48000,channels=1

these are `caps` in Gstreamer, their role is to constrain the 
data-formats being negotiated between the two elements that are 
on either side of them, so that two elements which are very 
flexible in what they can produce and consume can be restricted
to produce the format you actually need.

Next Steps
-----------

You likely don't want to spend the rest of your day looking at 
test patterns in vlc, so how do you go about doing more interesting
things?

* gst-inspect will let you see what elements are available, and what 
  properties those elements have
* you'll find lots of `gst-launch` samples on the internet
