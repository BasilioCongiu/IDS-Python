# Network Intrusion Detection System (IDS)

A real-time network traffic monitoring tool that intercepts packets, extracts metadata, and displays communication patterns through an interactive web dashboard — no terminal required.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Scapy](https://img.shields.io/badge/Scapy-2.5-green) ![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red) ![License](https://img.shields.io/badge/License-MIT-yellow)

> ⚠️ **Note:** Packet sniffing requires root/administrator privileges. Run with `sudo` on Linux/macOS.

---

## Features

- Live packet capture with per-protocol filtering (TCP, UDP, ICMP, SSH, FTP…)
- Metadata extraction: Source/Destination IP, Protocol, Packet Size, Timestamp
- Real-time Streamlit dashboard with auto-refresh
- Thread-safe architecture with zero UI blocking
- Constant memory footprint via a configurable Sliding Window

---

## System Architecture

The project follows the **Separation of Concerns** principle, split into three independent modules:

| Module | Responsibility |
|---|---|
| `capture.py` | Raw packet sniffing via Scapy |
| `analyzer.py` | Metadata extraction and enrichment |
| `app.py` | Streamlit dashboard and state management |

```
[ Network Interface ]
        │
        ▼
[ capture.py ] ──(Thread-Safe Queue)──▶ [ analyzer.py ] ──▶ [ app.py / Dashboard ]
```

---

## Technical Challenges & Solutions

### 1. Concurrency & Multi-Threading
Packet sniffing is a continuous, blocking operation. Running it on the same thread as the UI would cause freezes and packet loss.

**Solution:** A dedicated **Capture Thread** handles the raw stream, while a separate **Analyzer Thread** processes data — keeping the UI fully responsive at all times.

### 2. Thread-Safe Communication
Sharing mutable data between threads risks Race Conditions and data corruption.

**Solution:** A **Thread-Safe Queue** acts as a buffer between threads. The sniffer enqueues packets; the analyzer dequeues and processes them — no locks, no deadlocks.

### 3. Streamlit State Persistence
Streamlit reruns the entire script on every user interaction, which would normally restart the sniffing threads and lose all captured data.

**Solution:** `st.session_state` is used to persist thread objects and the data buffer across reruns, ensuring the capture process is never interrupted.

### 4. Memory Management
Continuous monitoring without limits leads to unbounded memory growth.

**Solution:** A **Sliding Window** retains only the last *N* packets in memory, discarding the oldest as new ones arrive — keeping the footprint constant and predictable.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/network-ids.git
cd network-ids

# Install dependencies
pip install -r requirements.txt
```

**Requirements:**
- Python 3.10+
- Scapy 2.5+
- Streamlit 1.x

---

## Usage

```bash
# Linux / macOS (root required for raw socket access)
sudo streamlit run app.py

# Windows (run terminal as Administrator)
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## Testing

### A. Internal Traffic (ICMP)
```bash
ping google.com
```
The dashboard should immediately show ICMP packets directed at Google's IP.

### B. Stress Test — High-Volume UDP Flood
```bash
# Linux only — requires hping3
sudo hping3 --udp --flood 127.0.0.1
```
Observe how the Sliding Window keeps memory usage flat during the spike.

### C. Protocol Verification
Connect to an SSH or FTP server and watch the `Protocol` field update in real time on the dashboard.

---

## What I Learned

- How to design a **concurrent, event-driven pipeline** in Python using threads and queues
- The trade-offs of different **inter-thread communication** strategies (shared memory vs. queues)
- How to manage **stateful background processes** inside a reactive UI framework like Streamlit
- The importance of **bounded data structures** in long-running monitoring systems

---

## Known Limitations & Future Improvements

- [ ] **Root requirement** — raw socket access mandates elevated privileges; a possible mitigation is using `libpcap` with appropriate capabilities set
- [ ] **No persistent storage** — packet history is lost on restart; adding a SQLite backend would fix this
- [ ] **Single interface** — currently captures on the default interface only; multi-interface support is planned
- [ ] **No alerting** — a rule-based alert system (e.g., port scan detection, traffic anomalies) would make this production-ready

---

## Tech Stack

| Layer | Technology |
|---|---|
| Packet Capture | [Scapy](https://scapy.net/) 2.5 |
| Web Dashboard | [Streamlit](https://streamlit.io/) 1.x |
| Concurrency | Python `threading` + `queue` |
| Language | Python 3.10+ |