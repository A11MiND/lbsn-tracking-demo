# LBSN Tracking Project - COMP5355

## Project Overview

This project aims to analyze the traffic of Location-Based Social Network (LBSN) apps to identify privacy leakages (plaintext HTTP location data) and demonstrate user tracking capabilities.

## Project Structure

- `pcap_files/`: Store your captured traffic files here.
- `scripts/`: Python scripts for analysis and scanning.
- `docs/`: Documentation and findings.

## Step 1: App Selection

Select 3 apps that use location features. Avoid apps mentioned in course slides.

**Categories to explore:**

- **Dating Apps**: Often broadcast precise distance or location.
- **Local Social/Chat**: "People Nearby" features.
- **Niche Booking Apps**: Local delivery or taxi apps might have weaker security than global giants like Uber.

## Step 2: Traffic Capture Setup

### Option A: Android Emulator (Easier)

1. Install **Android Studio** or **Genymotion**.
2. Configure the emulator to route traffic through your host machine.
3. Run **Wireshark** on your host machine, listening on the virtual network adapter.

### Option B: Physical Device (Real World)

1. Set up a **Mobile Hotspot** on your laptop.
2. Connect your phone to the hotspot.
3. Run **Wireshark** on the laptop, listening on the hotspot interface.

## Step 3: Analysis

1. Start capturing in Wireshark.
2. Open the target app and perform location-based actions (refresh "nearby", book a ride).
3. Stop capture and save as `.pcap`.
4. Run the analysis script:

   ```bash
   python scripts/analyze_pcap.py pcap_files/your_capture.pcap
   ```

## Step 4: Modification & Tracking

If you find an app sending coordinates (e.g., `lat=22.31&lon=114.16`) in HTTP:

1. **Verify**: Use a proxy tool like **MITMProxy** or **Burp Suite** to intercept the request, change the coordinates to a different city, and see if the app returns data for that new location.
2. **Scan**: Use the `scanner_template.py` to automate requests over a grid (e.g., covering Hong Kong) to map out users.

## Disclaimer

This project is for educational purposes only (COMP5355). Do not use these techniques to track real users without consent outside of the scope of this coursework.
