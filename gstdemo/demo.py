#! /usr/bin/env python
import logging
from . import pipeline
from gi.repository import GObject
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
log = logging.getLogger('gstreamer-demo')


CAMERA_VIDEO_FRAGMENT = [
    'v4l2src', '!',
    'videorate','!',
    'videoscale','!',
        
]

TEST_VIDEO_FRAGMENT = [
    # generate some video test output
    'videotestsrc', 'name=videotest', 'pattern=0', '!',
]
VIDEO_ENCODE_FRAGMENT = [
    # make it NTSC SD content
    'video/x-raw,framerate=30000/1001,width=720,height=480', '!',
    # encode with x264 (note: you may require a license to deploy this!)
    # Note that *this* element uses kbps for bitrate, some use bps
    'x264enc', 'bitrate=256', '!', 
    # Send it to the MPEG TS muxer we'll define later with a PID 
    # of 65 (the sink name determines the PID)
    'muxer.sink_65',
]
TEST_AUDIO_FRAGMENT = [
    # setup a parallel pipeline for audio...
    'audiotestsrc', '!',
    # parameters are high-quality monoaural audio
    'audio/x-raw,rate=48000,channels=1', '!',
    # encoded as AAC for compatibility with HLS
    'avenc_aac', 'bitrate=32000', '!',
    # again, send it into the muxer, this time on sink/pid 66
    'muxer.sink_66',
]

MUXING_FRAGMENT = [
    # Note that there is *no* '!' between framents! 
    # We're going to link the fragments with named references
    
    # package all streams into an MPEG TS container format
    'mpegtsmux', 
        # we use this name in the other pipeline fragments to route 
        # the content into this particular element...
        'name=muxer', 
        # silly example, here we say video (65) and audio (66) should 
        # be mapped into the same program with program number 10 (instead 
        # of the default program number 1). This isn't in any way necessary,
        # it just shows how to use "GstStructure" instances...
        # The sink-name were defined in the pipe operations that sent the 
        # content into the muxer...
        'prog-map=program_map,sink_65=10,sink_66=10',
        # Note that currently we have no way to specify the 
        # PIDs on the TS outputs, not a concern for HLS, but 
        # a concern for multicast video setups...
        '!',
    # dump to an HLS playlist/video-file...
    'hlssink',
        'location=/var/www/segment-%05d.ts',
        'playlist-location=/var/www/index.m3u8',
        'max-files=20',
        'target-duration=15',
]

SAMPLE_PIPELINE = (
    TEST_VIDEO_FRAGMENT + 
    VIDEO_ENCODE_FRAGMENT + 
    TEST_AUDIO_FRAGMENT + 
    MUXING_FRAGMENT
)

CAMERA_PIPELINE = (
    CAMERA_VIDEO_FRAGMENT + 
    VIDEO_ENCODE_FRAGMENT + 
    TEST_AUDIO_FRAGMENT + 
    MUXING_FRAGMENT
)

def get_options():
    import argparse
    parser = argparse.ArgumentParser( 
        description='Demonstrates GStreamer Python API' 
    )
    parser.add_argument(
        '-c','--camera',
        help = 'Use /dev/video0 as the video source',
        default = False,
        action = 'store_true',
    )
    return parser

def main():
    logging.basicConfig( level=logging.INFO )
    options = get_options().parse_args()
    Gst.init_check(None)
    command = SAMPLE_PIPELINE
    if options.camera:
        command = CAMERA_PIPELINE
    pipe = pipeline.Pipe( 'sample', command )
    pipe.run()
    def rotate_pattern(*args,**named):
        videotest = pipe.components.videotest
        if not videotest:
            return
        pattern = videotest.get_property( 'pattern' )
        pattern = (pattern + 1)%24
        videotest.set_property( 'pattern', pattern )
        GObject.timeout_add( 100, rotate_pattern )
    rotate_pattern()
    log.info("Muxer: %s", pipe.components.muxer)
    pipeline.LOOP.run()

if __name__ == "__main__":
    main()
