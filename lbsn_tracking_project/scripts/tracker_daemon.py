import requests
import time
import sqlite3
import datetime
import os

# ==========================================
# CONFIGURATION
# ==========================================

TARGET_URL = "https://api.flytaxiapp.com/v6/gps/get_user_nearby_drivers"

HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 3 Build/SP2A.220505.008)",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "PHPSESSID=3clulv7sodl7v0t050duag5miu; AWSALB=HxU4n3wk1vr6PjKNKPzEXaAXYvvIW6klxr2j7LsgjcaJLz9lPKrWflE+Ige0/1xNChdv+Djb4XD9EUx/UkvqPIhfXy3zEs92jD7XwiCxNImwlHaFtBZXcFRNrATJ; AWSALBCORS=HxU4n3wk1vr6PjKNKPzEXaAXYvvIW6klxr2j7LsgjcaJLz9lPKrWflE+Ige0/1xNChdv+Djb4XD9EUx/UkvqPIhfXy3zEs92jD7XwiCxNImwlHaFtBZXcFRNrATJ"
}

BASE_PAYLOAD = {
    "access_token": "RzViMXl2RmFuSlV1TUluRFRBTUFuNjJqNHRoNHQzUjVPc3Rka1lKbGdVYz0",
    "uid": "4342015",
    "ct_list": "1",
    "app_list": "32,33,37",
    "lang": "1",
    "city_id": "1"
}

# 监控区域：选择一个较小的住宅区，例如沙田第一城附近
# 这样可以减少请求量，专注于发现"常驻车辆"
MONITOR_LAT = 22.387
MONITOR_LON = 114.200
RADIUS_METERS = 2000 # 覆盖周边 2km

DB_FILE = "tracking_data.db"
SCAN_INTERVAL = 600 # 每 10 分钟扫一次

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS drivers
                 (timestamp TEXT, lat REAL, lng REAL, direction TEXT, speed TEXT)''')
    conn.commit()
    return conn

def scan_once(conn):
    print(f"[*] Scanning at {datetime.datetime.now()}...")
    
    payload = BASE_PAYLOAD.copy()
    payload["lat"] = str(MONITOR_LAT)
    payload["lng"] = str(MONITOR_LON)
    
    try:
        response = requests.post(TARGET_URL, headers=HEADERS, data=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "driver_list" in data["data"]:
                drivers = data["data"]["driver_list"]
                print(f"    -> Found {len(drivers)} drivers.")
                
                c = conn.cursor()
                timestamp = datetime.datetime.now().isoformat()
                
                for d in drivers:
                    c.execute("INSERT INTO drivers VALUES (?, ?, ?, ?, ?)",
                              (timestamp, d['lat'], d['lng'], d['direction'], d['speed']))
                conn.commit()
            else:
                print("    -> No drivers found.")
        else:
            print(f"    -> Error: {response.status_code}")
            
    except Exception as e:
        print(f"    -> Request failed: {e}")

def main():
    print(f"[*] Starting Long-Term Tracker Daemon")
    print(f"[*] Saving to {DB_FILE}")
    print(f"[*] Press Ctrl+C to stop")
    
    conn = init_db()
    
    try:
        while True:
            scan_once(conn)
            print(f"[*] Sleeping for {SCAN_INTERVAL} seconds...")
            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        print("\n[*] Stopping tracker...")
        conn.close()

if __name__ == "__main__":
    main()
