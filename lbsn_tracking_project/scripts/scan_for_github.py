import requests
import csv
import os
import datetime
import sys

# ================= CONFIG =================
# 目标：香港理工大学 (PolyU) 附近
TARGET_LAT = 22.3043
TARGET_LON = 114.1798
# 文件保存路径
DATA_FILE = "data/driver_history.csv"

# API 配置
URL = "https://api.flytaxiapp.com/v6/gps/get_user_nearby_drivers"
HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 3 Build/SP2A.220505.008)",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "PHPSESSID=3clulv7sodl7v0t050duag5miu; AWSALB=HxU4n3wk1vr6PjKNKPzEXaAXYvvIW6klxr2j7LsgjcaJLz9lPKrWflE+Ige0/1xNChdv+Djb4XD9EUx/UkvqPIhfXy3zEs92jD7XwiCxNImwlHaFtBZXcFRNrATJ"
}
PAYLOAD = {
    "access_token": "RzViMXl2RmFuSlV1TUluRFRBTUFuNjJqNHRoNHQzUjVPc3Rka1lKbGdVYz0",
    "uid": "4342015",
    "ct_list": "1",
    "app_list": "32,33,37",
    "lang": "1",
    "city_id": "1",
    "lat": str(TARGET_LAT),
    "lng": str(TARGET_LON)
}

def run_scan():
    # 确保 data 目录存在
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # 如果文件不存在，写入表头
    file_exists = os.path.isfile(DATA_FILE)
    
    print(f"[*] Scanning area: {TARGET_LAT}, {TARGET_LON}")
    
    try:
        resp = requests.post(URL, headers=HEADERS, data=PAYLOAD, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            drivers = data.get("data", {}).get("driver_list", [])
            
            print(f"[*] Found {len(drivers)} drivers")
            
            with open(DATA_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["timestamp", "lat", "lng", "direction", "speed"])
                
                now = datetime.datetime.now().isoformat()
                for d in drivers:
                    # 简单的去重逻辑可以放在分析阶段做，这里只管存
                    writer.writerow([now, d['lat'], d['lng'], d['direction'], d['speed']])
        else:
            print(f"[!] API Error: {resp.status_code}")
            sys.exit(1)
            
    except Exception as e:
        print(f"[!] Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scan()
