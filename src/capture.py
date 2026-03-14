import threading
from scapy.all import sniff
from scapy.layers.inet import IP


class PacketCapture:
    """
    PacketCapture is responsible for intercepting network packets from
    a given interface and forwarding them to a shared queue.

    This module only performs packet acquisition and does not process data.
    """

    def __init__(self, packet_queue):
        self.packet_queue = packet_queue
        self.stop_event = threading.Event()

    def start_capture(self, interface):
        """
        Starts the packet capture in a separate daemon thread.
        """
        thread = threading.Thread(
            target=self._run,
            args=(interface,),
            daemon=True
        )
        thread.start()

    def _run(self, interface):
        """
        Internal capture loop using Scapy sniff().
        """

        sniff(
            iface=interface,
            prn=self._callback,
            store=False,
            stop_filter=lambda _: self.stop_event.is_set()
        )

    def _callback(self, packet):
        """
        Callback executed for every captured packet.
        Only IP packets are forwarded to the analysis queue.
        """

        if packet.haslayer(IP):
            self.packet_queue.put(packet)

    def stop(self):
        """
        Signals the capture thread to stop.
        """
        self.stop_event.set()