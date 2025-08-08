#!/usr/bin/env python3

import sys
import raid_attendance_report
from raid_config import ALL_RAIDS

# Test script to discover actual zone IDs
def discover_zone_ids():
    print("🔍 Discovering actual zone IDs from Warcraft Logs...")
    
    api = raid_attendance_report.WarcraftLogsAPI(
        raid_attendance_report.CLIENT_ID, 
        raid_attendance_report.CLIENT_SECRET
    )
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    # Get attendance data
    all_raids = api.get_all_guild_attendance(784174, days=30)
    
    # Collect unique zone IDs and names
    zones = {}
    for raid in all_raids:
        zone = raid.get('zone', {})
        zone_id = zone.get('id')
        zone_name = zone.get('name', 'Unknown')
        
        if zone_id and zone_name:
            zones[zone_id] = zone_name
    
    print("\n📋 Actual Zone IDs found:")
    print("=" * 50)
    for zone_id, zone_name in sorted(zones.items()):
        print(f"  {zone_id:4d}: {zone_name}")
    
    print(f"\n📊 Total unique zones found: {len(zones)}")

if __name__ == "__main__":
    discover_zone_ids()
