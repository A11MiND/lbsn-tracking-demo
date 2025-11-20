import requests
import time
import json
import os

# ==========================================
# CONFIGURATION
# ==========================================

# 目标 API URL
TARGET_URL = "https://api.flytaxiapp.com/v6/gps/get_user_nearby_drivers"

# 请求头 (从你的截图提取)
HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 3 Build/SP2A.220505.008)",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    # 注意：Cookie 可能会过期，如果脚本失效，请重新抓包更新这里的 Cookie
    "Cookie": "PHPSESSID=3clulv7sodl7v0t050duag5miu; AWSALB=HxU4n3wk1vr6PjKNKPzEXaAXYvvIW6klxr2j7LsgjcaJLz9lPKrWflE+Ige0/1xNChdv+Djb4XD9EUx/UkvqPIhfXy3zEs92jD7XwiCxNImwlHaFtBZXcFRNrATJ; AWSALBCORS=HxU4n3wk1vr6PjKNKPzEXaAXYvvIW6klxr2j7LsgjcaJLz9lPKrWflE+Ige0/1xNChdv+Djb4XD9EUx/UkvqPIhfXy3zEs92jD7XwiCxNImwlHaFtBZXcFRNrATJ"
}

# 基础 Payload (从你的请求提取)
# lat 和 lng 会在循环中动态替换
BASE_PAYLOAD = {
    "access_token": "RzViMXl2RmFuSlV1TUluRFRBTUFuNjJqNHRoNHQzUjVPc3Rka1lKbGdVYz0",
    "uid": "4342015",
    "ct_list": "1",
    "app_list": "32,33,37",
    "lang": "1",
    "city_id": "1"
}

# 扫描范围：香港 (大致矩形范围)
# 左上角 (西北): 22.56, 113.83
# 右下角 (东南): 22.15, 114.40
HK_LAT_START = 22.40 # 稍微缩小一点范围以节省测试时间，你可以改回 22.56
HK_LAT_END = 22.20
HK_LON_START = 114.10
HK_LON_END = 114.30

# 步长 (度)。0.01 度大约是 1.1 公里。
# 步长越小，扫描越密，但请求次数越多。
STEP_SIZE = 0.02 

def scan_grid():
    print(f"[*] Starting scan of Hong Kong area...")
    print(f"[*] Target: {TARGET_URL}")
    
    current_lat = HK_LAT_START
    drivers_found = []
    unique_locations = set()

    total_requests = 0
    
    # 简单的网格遍历
    lat = HK_LAT_START
    while lat > HK_LAT_END:
        lon = HK_LON_START
        while lon < HK_LON_END:
            
            # 构造当前请求的 Payload
            payload = BASE_PAYLOAD.copy()
            payload["lat"] = str(lat)
            payload["lng"] = str(lon)
            
            try:
                print(f"[*] Probing: {lat:.4f}, {lon:.4f} ... ", end="")
                
                # 发送 POST 请求
                response = requests.post(TARGET_URL, headers=HEADERS, data=payload, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # 解析响应
                        # 结构: data -> driver_list -> [ {lat, lng, ...} ]
                        if "data" in data and "driver_list" in data["data"]:
                            driver_list = data["data"]["driver_list"]
                            count = 0
                            for driver in driver_list:
                                # 由于没有司机ID，我们用 "lat,lng" 组合作为唯一标识来去重
                                # 注意：这并不完美，如果两个司机在同一位置会被当成一个，但在移动车辆中概率较小
                                d_lat = driver.get("lat")
                                d_lng = driver.get("lng")
                                unique_key = f"{d_lat},{d_lng}"
                                
                                if unique_key not in unique_locations:
                                    unique_locations.add(unique_key)
                                    drivers_found.append(driver)
                                    count += 1
                            print(f"Found {count} new drivers (Total unique: {len(drivers_found)})")
                        else:
                            print("No drivers data.")
                    except json.JSONDecodeError:
                        print("Response is not JSON.")
                else:
                    print(f"Error: {response.status_code}")

            except Exception as e:
                print(f"Request failed: {e}")

            # 礼貌延时，防止被封 IP
            time.sleep(1) 
            total_requests += 1
            
            lon += STEP_SIZE
        
        lat -= STEP_SIZE

    print(f"\n[*] Scan complete.")
    print(f"[*] Total Requests: {total_requests}")
    print(f"[*] Total Unique Drivers Found: {len(drivers_found)}")
    
    # 保存结果
    output_file = "flytaxi_drivers.json"
    with open(output_file, "w") as f:
        json.dump(drivers_found, f, indent=4)
    
    print(f"[*] Data saved to {output_file}")

if __name__ == "__main__":
    scan_grid()
