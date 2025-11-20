# LBSN Tracking & Privacy Analysis Project (COMP5355)

## 🚨 Project Overview
This project demonstrates a significant privacy leakage in a popular Location-Based Social Network (LBSN) app used for taxi hailing in Hong Kong. 

By analyzing the app's network traffic, we identified an API endpoint that leaks **precise GPS coordinates** of drivers without adequate authentication or encryption. We exploited this vulnerability to implement a **"Scan One City"** attack, allowing us to track drivers' movements across Hong Kong in real-time.

## 🛠 Methodology

### 1. Vulnerability Discovery
- **Tools**: Mitmproxy, Genymotion Android Emulator.
- **Finding**: The API endpoint `/v6/gps/get_user_nearby_drivers` accepts arbitrary latitude/longitude parameters and returns a list of nearby drivers with high-precision coordinates, direction, and speed.
- **Exploit**: By modifying the request parameters (Location Spoofing), an attacker can query any location in the world.

### 2. Automated City-wide Scanning
- We developed a Python script (`scripts/scan_for_github.py`) that systematically queries 6 major districts in Hong Kong:
  - PolyU / Hung Hom
  - Mong Kok
  - Tsim Sha Tsui
  - Central
  - Causeway Bay
  - Sha Tin
- This simulates a "God View" surveillance system.

### 3. Persistent Data Collection (GitHub Actions)
- To fulfill the requirement of **"Profiling Users"**, we utilized **GitHub Actions** as a cloud-based scanner.
- **Workflow**: The scanner runs automatically **every 30 minutes**.
- **Storage**: Data is appended to `data/driver_history.csv` and committed back to the repository.
- This allows for long-term data collection without maintaining a local server.

### 4. Privacy Profiling (Clustering Analysis)
- Although the API does not return a unique User ID, we employ **Spatiotemporal Clustering**.
- By analyzing the `driver_history.csv` data, we can identify "stationary points" (Speed = 0) that appear frequently at specific times (e.g., late night).
- **Goal**: Infer sensitive locations such as **home addresses** or **regular parking spots** based on these clusters.

## 📂 Project Structure

```
.
├── .github/workflows/      # CI/CD configuration for automated scanning
├── data/                   # Collected driver location data (CSV)
├── scripts/
│   ├── scan_for_github.py  # Main scanning script (City-wide sampling)
│   ├── analyze_tracks.py   # Analysis script for clustering & profiling
└── README.md
```

## 🚀 How to Analyze the Data

1. **Wait for Data**: The GitHub Action collects data every 30 minutes. Let it run for a few days.
2. **Download Data**: Pull the latest `data/driver_history.csv` from the repository.
3. **Run Analysis**:
   ```bash
   python scripts/analyze_tracks.py
   ```
   This script will output the top suspected "Home Locations" based on the collected data.

## ⚠️ Disclaimer
This project is for **educational and research purposes only** (COMP5355 Coursework). All data collected is anonymized where possible. Do not use these techniques to track real individuals for malicious purposes.
