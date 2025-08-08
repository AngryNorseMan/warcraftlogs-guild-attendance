# Raid Configuration File for Attendance Report Generator

# All available raids/dungeons with their zone IDs (Classic Fresh Anniversary)
ALL_RAIDS = {
    # 40-man raids
    1028: "Molten Core",
    1034: "Blackwing Lair", 
    1035: "Temple of Ahn'Qiraj",  # AQ40
    
    # 20-man raids  
    1029: "Onyxia",
    1030: "Zul'Gurub",
    1031: "Ruins of Ahn'Qiraj",  # AQ20
    
    # Add Naxxramas when it becomes available
    # 1036: "Naxxramas",
}

# Predefined raid sets for easy filtering
RAID_SETS = {
    "40man": [1028, 1034, 1035],  # All 40-man raids (MC, BWL, AQ40)
    "40man_no_ony": [1028, 1034, 1035],  # 40-man excluding Onyxia (same as above since Ony is 20-man)
    "20man": [1029, 1030, 1031],  # All 20-man raids (Ony, ZG, AQ20)
    "mc_only": [1028],  # Molten Core only
    "bwl_only": [1034],  # Blackwing Lair only
    "aq40_only": [1035],  # AQ40 only
    "ony_only": [1029],  # Onyxia only
    "zg_only": [1030],   # Zul'Gurub only
    "aq20_only": [1031], # AQ20 only
    "classic_40man": [1028, 1034],  # MC + BWL
    "all": list(ALL_RAIDS.keys()),  # All raids
}

# Default configuration
DEFAULT_CONFIG = {
    "guild_id": 784174,
    "days_to_analyze": 30,
    "output_file": "raid_attendance_report.csv",
    "included_raids": RAID_SETS["40man"],  # Default: All 40-man raids (MC, BWL, AQ40)
    "minimum_attendance_to_show": 0,  # Show all players regardless of attendance
}

# You can modify this to change the default behavior
CURRENT_CONFIG = DEFAULT_CONFIG.copy()
