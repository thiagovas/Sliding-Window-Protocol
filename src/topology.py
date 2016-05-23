"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."
        
        # Initialize topology
        Topo.__init__( self )
        
        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        leftSwitch = self.addSwitch( 's3' )
        rightSwitch = self.addSwitch( 's4' )
        
        # Add links
        self.addLink( leftHost, leftSwitch , b2=10, delay='10ms' )
        self.addLink( leftSwitch, rightSwitch, bw=1, delay='100ms' )
        self.addLink( rightSwitch, rightHost, bw=10, delay='10ms' )


topos = { 'mytopo': ( lambda: MyTopo() ) }
