import time
import sys
from queue import Queue

from capture import PacketCapture
from analyzer import PacketAnalyzer


def main():

    packet_queue = Queue()

    capture = PacketCapture(packet_queue)
    analyzer = PacketAnalyzer(packet_queue)

    print("Starting IDS in CLI mode")

    capture.start_capture(interface="lo")
    analyzer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        print("Stopping IDS")

        capture.stop()
        analyzer.stop()

        sys.exit(0)


if __name__ == "__main__":
    main()