from pox.core import core
from pox.lib.revent import *
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet, arp, ipv4

log = core.getLogger()

class HostDiscovery(EventMixin):
    def __init__(self):
        self.mac_to_port = {}
        self.host_db = {}  # {mac: (ip, dpid, port)}
        core.openflow.addListeners(self)
        log.info("Host Discovery Controller started")

    def _handle_ConnectionUp(self, event):
        log.info("Switch %s connected", dpidToStr(event.dpid))

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            return

        dpid = event.dpid
        in_port = event.port
        src_mac = str(packet.src)
        dst_mac = str(packet.dst)

        # Learn MAC to port mapping
        if dpid not in self.mac_to_port:
            self.mac_to_port[dpid] = {}
        self.mac_to_port[dpid][src_mac] = in_port

        # Host discovery via ARP
        arp_pkt = packet.find('arp')
        ip_pkt = packet.find('ipv4')

        if arp_pkt:
            src_ip = str(arp_pkt.protosrc)
            if src_mac not in self.host_db:
                self.host_db[src_mac] = (src_ip, dpid, in_port)
                log.info("[HOST JOIN] MAC=%s IP=%s Switch=%s Port=%s",
                         src_mac, src_ip, dpidToStr(dpid), in_port)
                self._print_host_db()

        elif ip_pkt:
            src_ip = str(ip_pkt.srcip)
            if src_mac not in self.host_db:
                self.host_db[src_mac] = (src_ip, dpid, in_port)
                log.info("[HOST JOIN] MAC=%s IP=%s Switch=%s Port=%s",
                         src_mac, src_ip, dpidToStr(dpid), in_port)

        # Forward packet
        if dst_mac in self.mac_to_port.get(dpid, {}):
            out_port = self.mac_to_port[dpid][dst_mac]
            # Install flow rule
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, in_port)
            msg.priority = 10
            msg.idle_timeout = 30
            msg.hard_timeout = 60
            msg.actions.append(of.ofp_action_output(port=out_port))
            event.connection.send(msg)
        else:
            # Flood
            out_port = of.OFPP_FLOOD

        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.in_port = in_port
        msg.actions.append(of.ofp_action_output(port=out_port))
        event.connection.send(msg)

    def _print_host_db(self):
        log.info("--- Host Database ---")
        for mac, (ip, dpid, port) in self.host_db.items():
            log.info("  MAC: %s | IP: %s | Switch: %s | Port: %s",
                     mac, ip, dpidToStr(dpid), port)
        log.info("---------------------")

def launch():
    core.registerNew(HostDiscovery)
