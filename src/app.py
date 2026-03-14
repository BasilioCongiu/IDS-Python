import streamlit as st
import pandas as pd
import time
import subprocess
import logging
from queue import Queue

from capture import PacketCapture
from analyzer import PacketAnalyzer


logging.basicConfig(level=logging.INFO)


def get_default_iface():
    """
    Detects the default network interface used for routing.

    This implements a basic network abstraction layer by
    querying the operating system routing table.
    """

    try:
        cmd = "ip route show | grep default | awk '{print $5}'"
        iface = subprocess.check_output(cmd, shell=True).decode().strip()

        if not iface:
            raise ValueError("Interface not detected")

        logging.info(f"Detected network interface: {iface}")
        return iface

    except Exception as e:

        logging.error(f"Interface detection failed: {e}")
        return "lo"


def main():

    st.set_page_config(
        page_title="IDS Live Monitor",
        layout="wide"
    )

    st.title("Network Intrusion Detection Monitor")

    # Initialize session state only once
    if "capture" not in st.session_state:

        st.session_state.packet_queue = Queue()

        st.session_state.capture = PacketCapture(
            st.session_state.packet_queue
        )

        st.session_state.analyzer = PacketAnalyzer(
            st.session_state.packet_queue
        )

        iface = get_default_iface()

        st.info(f"Monitoring interface: {iface}")

        st.session_state.capture.start_capture(interface=iface)
        st.session_state.analyzer.start()

    placeholder = st.empty()

    # Dashboard refresh loop
    while True:

        data = st.session_state.analyzer.get_summary()

        if data:

            df = pd.DataFrame(data)

            def highlight_suspicious(row):
                if row["Alert"] == "SUSPICIOUS":
                    return ["background-color: #ffcccc"] * len(row)
                return [""] * len(row)

            styled_df = df.style.apply(highlight_suspicious, axis=1)

            with placeholder.container():
                st.dataframe(styled_df, use_container_width=True)

        else:
            st.warning("Waiting for network traffic...")

        time.sleep(1)


if __name__ == "__main__":
    main()