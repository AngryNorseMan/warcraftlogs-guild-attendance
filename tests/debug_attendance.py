#!/usr/bin/env python3

import raid_attendance_report

def debug_attendance():
    api = raid_attendance_report.WarcraftLogsAPI(
        raid_attendance_report.CLIENT_ID, 
        raid_attendance_report.CLIENT_SECRET
    )
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    # Get just one raid to examine the data structure
    raids, has_more = api.get_guild_attendance(784174, page=1)
    
    if raids:
        raid = raids[0]  # Look at the first raid
        print("🔍 Full raid data structure:")
        print(f"Zone: {raid.get('zone')}")
        print(f"Players: {raid.get('players', [])}")
        print(f"Code: {raid.get('code')}")
        print(f"StartTime: {raid.get('startTime')}")
        
        # Check if players list is empty or structured differently
        players = raid.get('players', [])
        print(f"\nPlayer count: {len(players)}")
        if players:
            print(f"First player: {players[0]}")
        else:
            print("No players found in this raid")
            print("Full raid keys:", list(raid.keys()))
    else:
        print("No raids found")

if __name__ == "__main__":
    debug_attendance()
