#!/usr/bin/env python3

# Simple test to check the script functionality
try:
    print("Testing imports...")
    from raid_config import ALL_RAIDS, RAID_SETS, CURRENT_CONFIG
    print("✓ Config imported successfully")
    
    print(f"Available raid sets: {list(RAID_SETS.keys())}")
    print(f"40man_no_ony includes: {RAID_SETS['40man_no_ony']}")
    
    import raid_attendance_report
    print("✓ Main script imported successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
