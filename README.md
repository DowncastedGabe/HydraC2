# Hydra C2

An academic Command & Control (C2) ecosystem built in Python with end-to-end Fernet encryption, dynamic memory processing (fileless), and resilient beaconing handlers.

This project was developed strictly for educational, research, and academic laboratory purposes in Information Security and Software Engineering. The ecosystem demonstrates the internal architecture of a secure remote access implant and a centralized control panel.

---

## 🚀 Technical Highlights & Architecture

The primary focus of development was to move beyond a simple terminal script and apply real-world industry standards for resilience and data protection:

* **End-to-End Encryption (E2E):** All traffic traveling between the Agent and the C2 Server passes through a symmetric encryption middleware using the **Fernet (AES-128-CBC + HMAC-SHA256)** standard. Network packet inspections (such as Wireshark) will only see opaque, unreadable payloads.
* **Memory-Only Processing (Fileless):** The graphical capture module (*screenshot*) processes and transmits binary chunks directly through the host's RAM. The image never touches the target's hard drive, minimizing forensic artifacts and file I/O footprints.
* **Resilient Beaconing:** The agent features an adaptive reconnection loop. If the panel experiences a drop or network fluctuation, the agent goes silent and attempts to re-establish contact autonomously without freezing the host system or generating zombie processes.
* **Secrets Isolation:** Complete removal of fixed keys in the code (*hardcoded keys*). The ecosystem manages cryptographic tokens dynamically via Operating System environment variables (`os.getenv`).

---

## 📁 Project Structure

```text
├── src/
│   ├── c2_server/
│   │   ├── main.py        # Interactive panel initializer
│   │   └── core.py        # C2 socket listener engine
│   ├── agent/
│   │   ├── modules/
│   │   │   └── screenshot.py # Graphical capture with runtime import
│   │   ├── main.py        # Remote agent initializer
│   │   └── core.py        # Beaconing logic and implant execution
│   └── utils/
│       └── crypto.py      # Shared encryption helper
├── .env.example           # Environment variables template
└── requirements.txt       # Project dependencies
