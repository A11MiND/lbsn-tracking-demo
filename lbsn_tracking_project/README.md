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

## 🔄 How to Update Expired Token

The `access_token` used in the scanning script may expire periodically (e.g., every 24 hours). If the GitHub Action fails (shows a red cross), follow these steps to update it:

1. **Capture New Token**:
   - Open **Genymotion** and **Mitmproxy**.
   - Refresh the FlyTaxi app to trigger a new request.
   - In Mitmproxy (`http://127.0.0.1:8081`), find the request to `api.flytaxiapp.com`.
   - Copy the value of `access_token` from the request body.

2. **Update Script**:
   - Open `lbsn_tracking_project/scripts/scan_for_github.py`.
   - Replace the value of `access_token` in the `BASE_PAYLOAD` dictionary with the new token.

3. **Push Changes**:
   - Run the following commands in your terminal to update the script on GitHub:
     ```bash
     # First, pull the latest data to avoid conflicts
     git pull --rebase origin main
     
     # Then commit and push the new token
     git add lbsn_tracking_project/scripts/scan_for_github.py
     git commit -m "Update expired access token"
     git push origin main
     ```

## ⚠️ Disclaimer
This project is for **educational and research purposes only** (COMP5355 Coursework). All data collected is anonymized where possible. Do not use these techniques to track real individuals for malicious purposes.
