# ============================================================
# Host Discovery Service using POX SDN Controller
# Course: Computer Networks - UE24CS252B
# Description: Automatically detects and maintains a list of
#              hosts in the SDN network using OpenFlow
# ============================================================

from pox.core import core
from pox.lib.revent import *
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet, arp, ipv4

# Get logger instance for this module
log = core.getLogger()

class HostDiscovery(EventMixin):
    """
    Host Discovery Controller
    - Listens for PacketIn events from connected switches
    - Learns MAC-to-port mappings dynamically
    - Discovers hosts via ARP and IPv4 packets
    - Maintains a host database with MAC, IP, Switch, Port
    - Installs flow rules for known destinations
    """

    def __init__(self):
        # Dictionary to store MAC-to-port mappings per switch
        # Format: {dpid: {mac: port}}
        self.mac_to_port = {}

        # Host database to store discovered hosts
        # Format: {mac: (ip, dpid, port)}
        self.host_db = {}

        # Register this controller to listen to OpenFlow events
        core.openflow.addListeners(self)
        log.info("Host Discovery Controller started")

    def _handle_ConnectionUp(self, event):
        """
        Called when a switch connects to the controller.
        Logs the switch DPID (datapath ID).
        """
        log.info("Switch %s connected", dpidToStr(event.dpid))

    def _handle_PacketIn(self, event):
        """
        Called when a switch sends a packet to the controller.
        This happens when no matching flow rule exists.
        Handles:
        - MAC learning
        - Host discovery via ARP/IP
        - Flow rule installation
        - Packet forwarding
        """
        # Parse the incoming packet
        packet = event.parsed
        if not packet.parsed:
            # Ignore incomplete packets
            return

        # Extract switch ID and incoming port
        dpid = event.dpid
        in_port = event.port

        # Extract source and destination MAC addresses
        src_mac = str(packet.src)
        dst_mac = str(packet.dst)

        # --- MAC LEARNING ---
        # Learn which port this MAC address is reachable on
        if dpid not in self.mac_to_port:
            self.mac_to_port[dpid] = {}
        self.mac_to_port[dpid][src_mac] = in_port

        # --- HOST DISCOVERY ---
        # Try to extract ARP packet for host discovery
        arp_pkt = packet.find('arp')
        # Try to extract IPv4 packet for host discovery
        ip_pkt = packet.find('ipv4')

        if arp_pkt:
            # ARP packet — extract source IP
            src_ip = str(arp_pkt.protosrc)
            if src_mac not in self.host_db:
                # New host detected — add to database
                self.host_db[src_mac] = (src_ip, dpid, in_port)
                log.info("[HOST JOIN] MAC=%s IP=%s Switch=%s Port=%s",
                         src_mac, src_ip, dpidToStr(dpid), in_port)
                # Print updated host database
                self._print_host_db()

        elif ip_pkt:
            # IPv4 packet — extract source IP
            src_ip = str(ip_pkt.srcip)
            if src_mac not in self.host_db:
                # New host detected — add to database
                self.host_db[src_mac] = (src_ip, dpid, in_port)
                log.info("[HOST JOIN] MAC=%s IP=%s Switch=%s Port=%s",
                         src_mac, src_ip, dpidToStr(dpid), in_port)

        # --- PACKET FORWARDING ---
        if dst_mac in self.mac_to_port.get(dpid, {}):
            # Destination MAC is known — forward to specific port
            out_port = self.mac_to_port[dpid][dst_mac]

            # Install a flow rule so future packets don't come to controller
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, in_port)
            msg.priority = 10          # Higher priority than table-miss
            msg.idle_timeout = 30      # Remove rule after 30s of inactivity
            msg.hard_timeout = 60      # Remove rule after 60s regardless
            msg.actions.append(of.ofp_action_output(port=out_port))
            event.connection.send(msg)
        else:
            # Destination MAC unknown — flood to all ports
            out_port = of.OFPP_FLOOD

        # Send the current packet out
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.in_port = in_port
        msg.actions.append(of.ofp_action_output(port=out_port))
        event.connection.send(msg)

    def _print_host_db(self):
        """
        Prints the current host database to the log.
        Shows all discovered hosts with their details.
        """
        log.info("--- Host Database ---")
        for mac, (ip, dpid, port) in self.host_db.items():
            log.info("  MAC: %s | IP: %s | Switch: %s | Port: %s",
                     mac, ip, dpidToStr(dpid), port)
        log.info("---------------------")

def launch():
    """
    Entry point for POX controller.
    Registers the HostDiscovery application.
    """
    core.registerNew(HostDiscovery)
