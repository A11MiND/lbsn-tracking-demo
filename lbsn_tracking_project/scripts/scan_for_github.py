import requests
import csv
import os
import datetime
import sys

# ================= CONFIG =================
# 目标：扫描香港主要区域 (模拟 "Scan One City")
# 选取几个热点区域进行采样，以覆盖城市主要活动区
SCAN_LOCATIONS = [
    {"name": "PolyU/Hung Hom", "lat": 22.3043, "lng": 114.1798},
    {"name": "Mong Kok", "lat": 22.3193, "lng": 114.1694},
    {"name": "Tsim Sha Tsui", "lat": 22.2988, "lng": 114.1722},
    {"name": "Central", "lat": 22.2819, "lng": 114.1581},
    {"name": "Causeway Bay", "lat": 22.2800, "lng": 114.1850},
    {"name": "Sha Tin", "lat": 22.3820, "lng": 114.1920}
]

# 文件保存路径
DATA_FILE = "data/driver_history.csv"

# API 配置
URL = "https://api.flytaxiapp.com/v6/gps/get_user_nearby_drivers"
HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 3 Build/SP2A.220505.008)",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "PHPSESSID=3clulv7sodl7v0t050duag5miu; AWSALB=HxU4n3wk1vr6PjKNKPzEXaAXYvvIW6klxr2j7LsgjcaJLz9lPKrWflE+Ige0/1xNChdv+Djb4XD9EUx/UkvqPIhfXy3zEs92jD7XwiCxNImwlHaFtBZXcFRNrATJ"
}
BASE_PAYLOAD = {
    "access_token": "RzViMXl2RmFuSlV1TUluRFRBTUFuNjJqNHRoNHQzUjVPc3Rka1lKbGdVYz0",
    "uid": "4342015",
    "ct_list": "1",
    "app_list": "32,33,37",
    "lang": "1",
    "city_id": "1"
}

def run_scan():
    # 确保 data 目录存在
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # 如果文件不存在，写入表头
    file_exists = os.path.isfile(DATA_FILE)
    
    print(f"[*] Starting City-wide Scan (Sampled)...")
    
    all_drivers = []
    
    for loc in SCAN_LOCATIONS:
        print(f"[*] Scanning {loc['name']} ({loc['lat']}, {loc['lng']})...")
        
        payload = BASE_PAYLOAD.copy()
        payload["lat"] = str(loc["lat"])
        payload["lng"] = str(loc["lng"])
        
        try:
            resp = requests.post(URL, headers=HEADERS, data=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                drivers = data.get("data", {}).get("driver_list", [])
                print(f"    -> Found {len(drivers)} drivers")
                all_drivers.extend(drivers)
            else:
                print(f"    -> [!] API Error: {resp.status_code}")
        except Exception as e:
            print(f"    -> [!] Failed: {e}")
            
    # 保存数据
    if all_drivers:
        with open(DATA_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "lat", "lng", "direction", "speed"])
            
            now = datetime.datetime.now().isoformat()
            for d in all_drivers:
                writer.writerow([now, d['lat'], d['lng'], d['direction'], d['speed']])
        print(f"[*] Saved {len(all_drivers)} records to {DATA_FILE}")
    else:
        print("[*] No drivers found in this scan cycle.")

if __name__ == "__main__":
    run_scan()
