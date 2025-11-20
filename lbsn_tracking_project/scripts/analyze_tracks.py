import sqlite3
import pandas as pd
from math import radians, cos, sin, asin, sqrt

DB_FILE = "tracking_data.db"

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r * 1000 # meters

def analyze():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found. Run tracker_daemon.py first.")
        return

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM drivers", conn)
    conn.close()
    
    print(f"[*] Loaded {len(df)} records.")
    
    # 1. 找出"静止"的车辆 (Speed = 0)
    # 注意：有些 API 返回的 speed 是字符串 "0"，有些是数字 0
    stationary = df[df['speed'].astype(str) == "0"]
    print(f"[*] Found {len(stationary)} stationary records.")
    
    # 2. 聚类分析 (简单的网格聚类)
    # 将经纬度保留 4 位小数 (约 11 米精度)，视为同一地点
    stationary['lat_round'] = stationary['lat'].astype(float).round(4)
    stationary['lng_round'] = stationary['lng'].astype(float).round(4)
    
    # 统计每个地点出现的次数
    location_counts = stationary.groupby(['lat_round', 'lng_round']).size().reset_index(name='counts')
    
    # 找出出现次数最多的地点 (Top 5)
    top_locations = location_counts.sort_values('counts', ascending=False).head(5)
    
    print("\n[*] Top 5 Suspected Home/Parking Locations:")
    for index, row in top_locations.iterrows():
        print(f"    Location: ({row['lat_round']}, {row['lng_round']}) - Seen {row['counts']} times")
        
        # 进一步分析该地点的出现时间段
        loc_records = stationary[
            (stationary['lat_round'] == row['lat_round']) & 
            (stationary['lng_round'] == row['lng_round'])
        ]
        
        # 提取小时
        loc_records['hour'] = pd.to_datetime(loc_records['timestamp']).dt.hour
        hours = loc_records['hour'].unique()
        hours.sort()
        print(f"    -> Active Hours: {hours}")
        
        # 判断是否像"家" (晚上出现)
        night_hours = [h for h in hours if h >= 22 or h <= 6]
        if len(night_hours) > 0:
            print(f"    -> [!] High Probability of HOME (Present at night)")
        else:
            print(f"    -> Likely a daytime parking spot")
            
    print("\n[*] Analysis Complete.")

if __name__ == "__main__":
    import os
    analyze()
