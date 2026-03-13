from scapy.all import sniff, IP, TCP
import threading
import queue

class PacketCapture: 

    """Handles network packet capturing asynchronously."""

    def __init__(self):

        # We use a thread-safe queue to pass packets from the sniffer to the analyzer

        self.packet_queue = queue.Queue()
        self.stop_event = threading.Event()

    def packet_callback(self, packet):

        """Callback invoked by Scapy for every captured packet."""
        # Only process packets containing both IP and TCP layers

        if IP in packet and TCP in packet:
            self.packet_queue.put(packet)

    def startcapture(self, interface="eth0"):

        """Starts sniffing in a separate thread to avoid blocking the main application."""
        # store=0 prevents packets from being kept in memory
        
        def capture_thread():
            sniff(iface=interface, prn=self.packet_callback, store=0, stop_filter=lambda _: self.stop_event.is_set())

        self.thread = threading.Thread(target=capture_thread)
        self.thread.start()
        
    def stop(self):

        """Signals the sniffer thread to stop and waits for it to join."""
        
        self.stop_event.set()
        self.thread.join()