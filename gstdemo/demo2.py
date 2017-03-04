#! /usr/bin/env python
import logging
from . import pipeline
from . import demo as previous
from gi.repository import GObject
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
log = logging.getLogger('gstreamer-demo')

GENERATOR_PIPELINE = [
    'videotestsrc', 'name=videotest', 'pattern=0', '!',
    'video/x-raw,framerate=30000/1001,width=720,height=480', '!',
    'x264enc', 'bitrate=256', '!', 
    'mpegtsmux', 
        'name=muxer', 
        'prog-map=program_map,sink_65=10,sink_66=10','!',
    'udpsink',
        'host=224.1.1.2',
        'port=8000',
        'multicast-iface=lo',
]


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
    command = [
        'udpsrc',
            'name=network',
            'address=224.1.1.2',
            'port=8000',
            'multicast-iface=lo',
            '!',
        'tsdemux',
            'name=demux',
            'emit-stats=true',
            '!',
        'fakesink',
    ]
    pipe = pipeline.Pipe( 'sample', command )
    pipe.run()
    pipe2 = pipeline.Pipe( 'generator', GENERATOR_PIPELINE)
    pipe2.run()
    def pad_added( bus, message ):
        log.info('pad added: %s', message)
    pipe.components.demux.connect( 'pad-added', pad_added )
    
    log.info("Muxer: %s", pipe.components.muxer)
    pipeline.LOOP.run()

if __name__ == "__main__":
    main()
