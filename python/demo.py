#! /usr/bin/env python
import logging
from gi.repository import GObject
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib
from gi.repository import Gst
log = logging.getLogger('gstreamer-demo')

class Pipe( object ):
    """Instance that runs a pipeline for us"""
    def __init__( self, pipe ):
        self.pipeline_command = pipe 
        self.pipeline = None
        self.state = Gst.State.NULL
    def run( self ):
        self.pipeline = Gst.parse_launchv( self.pipeline_command )
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect( "message", self.message )
        self.pipeline.set_state( Gst.State.PLAYING )
    def message( self, bus, message ):
        """Process a bus message from gstreamer"""
        message_name = message.type.get_name( message.type ).replace('-','_')
        method_name = 'message_%s'%(message_name,)
        method = getattr( self, method_name, None )
        if method:
            return method( bus, message )
        else:
            log.info("message: %s", message.type )
    def message_error(self, bus, message ):
        err, debug = message.parse_error()
        log.error( "Error reported, aborting: %s (debug=%s)", err, debug )
        LOOP.quit()

SAMPLE_PIPELINE = [
    # generate some video test output
    'videotestsrc', 'pattern=0', '!',
    # make it NTSC SD content
    'video/x-raw,framerate=30000/1001,width=720,height=480', '!',
    # encode with x264 (note: you may require a license to deploy this!)
    # Note that *this* element uses kbps for bitrate, some use bps
    'x264enc', 'bitrate=256', '!' 
    # package into an MPEG TS container format
    'mpegtsmux', '!',
    # dump to an HLS playlist/video-file...
    'hlssink',
        'location=/var/www/segment-%05d.ts',
        'playlist-location=/var/www/index.m3u8',
        'max-files=10',
        'target-duration=10',
]
        
def main():
    global LOOP
    LOOP = GObject.MainLoop()
    Gst.init_check(None)
    pipe = Pipe( SAMPLE_PIPELINE )
    pipe.run()
    LOOP.run()

if __name__ == "__main__":
    logging.basicConfig( level=logging.INFO )
    main()
