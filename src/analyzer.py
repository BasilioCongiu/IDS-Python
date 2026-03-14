import threading
import logging
import queue
from scapy.layers.inet import IP

# Configure IDS audit logging
logging.basicConfig(
    filename="ids_audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class PacketAnalyzer(threading.Thread):
    """
    PacketAnalyzer consumes packets from a shared queue,
    extracts relevant metadata and stores a limited
    sliding window of processed results.
    """

    def __init__(self, packet_queue):
        super().__init__(daemon=True)

        self.packet_queue = packet_queue
        self.data = []
        self._stop_event = threading.Event()

        # Static rule-based list of suspicious IP addresses
        self.suspicious_ips = [
            "192.168.1.50",
            "10.0.0.5",
            "10.111.23.8",
            "10.111.23.136"
        ]

    def run(self):
        """
        Thread execution loop that continuously consumes packets
        from the queue and performs analysis.
        """

        while not self._stop_event.is_set():

            try:
                pkt = self.packet_queue.get(timeout=1)

                if pkt.haslayer(IP):

                    src = pkt[IP].src
                    dst = pkt[IP].dst
                    proto = pkt.sprintf("%IP.proto%")

                    is_suspicious = (
                        src in self.suspicious_ips or
                        dst in self.suspicious_ips
                    )

                    # Log traffic events
                    if is_suspicious:
                        logging.warning(f"Suspicious traffic detected: {src} -> {dst}")
                    else:
                        logging.info(f"Traffic observed: {src} -> {dst}")

                    packet_info = {
                        "Src": src,
                        "Dst": dst,
                        "Proto": proto,
                        "Alert": "SUSPICIOUS" if is_suspicious else "OK"
                    }

                    self.data.append(packet_info)

                    # Sliding window to prevent memory growth
                    if len(self.data) > 20:
                        self.data.pop(0)

            except queue.Empty:
                continue

    def stop(self):
        """
        Stops the analyzer thread.
        """
        self._stop_event.set()

    def get_summary(self):
        """
        Returns the latest processed packet data.
        """
        return self.data