#! /usr/bin/env python
import logging, os
from gi.repository import GObject
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib
from gi.repository import Gst
log = logging.getLogger('gstreamer-demo')

class ComponentNamespace( object ):
    def __init__(self,pipeline):
        self.pipeline = pipeline 
    def __getattribute__(self, name ):
        if name != 'pipeline':
            return self.pipeline.get_child_by_name( name )
        return super(ComponentNamespace,self).__getattribute__(name)

class Pipe( object ):
    """Instance that runs a pipeline for us"""
    def __init__( self, name, pipe ):
        self.name = name
        self.pipeline_command = pipe 
        self.pipeline = None
        self.state = Gst.State.NULL
    def run( self ):
        try:
            self.pipeline = Gst.parse_launchv( self.pipeline_command )
        except GLib.Error as err:
            log.error("Failed to parse the pipeline: %s", err)
            log.info(
                " gst-launch --gst-debug=3 %s",
                " ".join( self.pipeline_command )
            )
            raise
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
    @property
    def components(self):
        return ComponentNamespace( self.pipeline )
    def message_error(self, bus, message ):
        err, debug = message.parse_error()
        log.error( "Error reported, aborting: %s (debug=%s)", err, debug )
        LOOP.quit()
    def message_state_changed(self, bus, message ):
        structure = message.parse_state_changed()
        newstate = structure.newstate
        if newstate != self.state:
            log.info('%s state: %s -> %s', self.name, self.state, newstate )
            self.state = newstate
    def message_stream_start(self, bus, message ):
        log.info("Stream started")
        for i,pad in enumerate(self.components.muxer.sinkpads):
            log.info("Muxer pad: %s", pad.name)

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

if os.path.exists('/dev/video0'):
    SAMPLE_PIPELINE = (
        CAMERA_VIDEO_FRAGMENT + 
        VIDEO_ENCODE_FRAGMENT + 
        TEST_AUDIO_FRAGMENT + 
        MUXING_FRAGMENT
    )
        
def main():
    global LOOP
    LOOP = GObject.MainLoop()
    Gst.init_check(None)
    pipe = Pipe( 'sample',SAMPLE_PIPELINE )
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
    LOOP.run()

if __name__ == "__main__":
    logging.basicConfig( level=logging.INFO )
    main()
