import sys
from scapy.all import *
from scapy.layers.http import HTTPRequest
import re

def analyze_pcap(pcap_file):
    print(f"[*] Loading {pcap_file}...")
    try:
        packets = rdpcap(pcap_file)
    except FileNotFoundError:
        print(f"[!] File {pcap_file} not found.")
        return

    print(f"[*] Scanned {len(packets)} packets. Searching for HTTP location leaks...")
    
    location_keywords = [b'lat', b'lon', b'lng', b'latitude', b'longitude', b'location', b'gps']
    found_leaks = False

    for packet in packets:
        if packet.haslayer(HTTPRequest):
            http_layer = packet[HTTPRequest]
            
            # Check Method (GET/POST)
            method = http_layer.Method.decode()
            host = http_layer.Host.decode() if http_layer.Host else "Unknown"
            path = http_layer.Path.decode() if http_layer.Path else ""
            
            full_url = f"{host}{path}"
            payload = bytes(packet[HTTPRequest].payload)
            
            # Check URL parameters and Body for keywords
            raw_data = path.encode() + b" " + payload
            
            for keyword in location_keywords:
                if keyword in raw_data.lower():
                    print(f"\n[!] POTENTIAL LEAK FOUND in {method} request to {host}")
                    print(f"    URL: {full_url}")
                    if payload:
                        print(f"    Payload: {payload[:100]}...") # Print first 100 bytes
                    
                    # Try to extract the specific values using regex
                    # Look for lat=12.34 or "lat":12.34
                    lat_matches = re.findall(rb'(?:lat|latitude)["\']?[:=]\s*["\']?(-?\d+\.\d+)', raw_data, re.IGNORECASE)
                    lon_matches = re.findall(rb'(?:lon|lng|longitude)["\']?[:=]\s*["\']?(-?\d+\.\d+)', raw_data, re.IGNORECASE)
                    
                    if lat_matches:
                        print(f"    -> Extracted Latitude: {lat_matches[0].decode()}")
                    if lon_matches:
                        print(f"    -> Extracted Longitude: {lon_matches[0].decode()}")
                        
                    found_leaks = True
                    break # Move to next packet if leak found in this one

    if not found_leaks:
        print("\n[-] No obvious plaintext HTTP location leaks found.")
        print("    Note: Traffic might be HTTPS (encrypted) or using non-standard keywords.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_pcap.py <path_to_pcap_file>")
    else:
        analyze_pcap(sys.argv[1])
