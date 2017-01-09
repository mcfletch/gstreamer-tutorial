#! /usr/bin/env python
import logging
from gi.repository import GObject
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib
from gi.repository import Gst
log = logging.getLogger(__name__)

LOOP = GObject.MainLoop()


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
