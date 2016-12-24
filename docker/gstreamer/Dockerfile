# Setup a Python environment with GStreamer for PyGI demos
FROM ubuntu:16.10

MAINTAINER Michael Fletcher <mcfletch@vrplumber.com>

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y \
    python3.5-dev \
    python3-gi \
    python3-gst-1.0 \
    gstreamer1.0-libav \
    gstreamer1.0-nice \
    gstreamer1.0-plugins-bad \ 
    gstreamer1.0-plugins-bad-faad \
    gstreamer1.0-plugins-bad-videoparsers \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-pulseaudio \
    gstreamer1.0-tools

CMD /usr/bin/python3.5 /var/python/demo.py
