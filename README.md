# WoW Guild Raid Attendance Report Generator

A Python tool that fetches guild raid attendance data from Warcraft Logs API and generates CSV reports for analyzing player attendance across raids.

## Setup

### Prerequisites
- Python 3.7+
- Warcraft Logs API credentials

### Get API Credentials
1. Go to [Warcraft Logs API Clients](https://www.warcraftlogs.com/api/clients/)
2. Click "Create Client"
3. Choose "Public Client" for the client type
4. **Important**: Make sure you're creating a **v2 API client** (not v1)
5. Note down your `Client ID` and `Client Secret`

> ⚠️ **Critical**: This tool requires Warcraft Logs **v2 API** credentials. v1 API credentials will not work.

### Environment Configuration
The application uses environment variables for API credentials to keep them secure.

## Features

- ✅ Fetches data from Warcraft Logs Fresh API (Classic Anniversary)
- ✅ Configurable raid filtering (40-man, 20-man, specific raids)
- ✅ Guild member filtering (excludes PUGs and non-guild players)
- ✅ Deduplication of multiple logs for the same raid on the same day
- ✅ CSV export with attendance percentages
- ✅ Command-line interface with multiple options
- ✅ Support for custom time periods
- ✅ Secure environment variable configuration
- ✅ Guild roster API integration

## Quick Start

### 1. Setup Environment
```bash
# Copy the environment template
cp .env.sample .env

# Edit .env and add your Warcraft Logs API credentials
# Get credentials from: https://www.warcraftlogs.com/api/clients/
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Reports
```bash
# Generate default report (40-man raids, no Onyxia, last 30 days)
python raid_attendance_report.py

# Generate guild members only report (excludes PUGs)
python raid_attendance_report.py --guild-members-only

# Generate Molten Core only report for last 7 days
python raid_attendance_report.py --raids mc_only --days 7

# Generate custom report with specific zones
python raid_attendance_report.py --zones 1028 1034 --output my_report.csv

# Generate BWL report for guild members only
python raid_attendance_report.py --raids bwl_only --guild-members-only --output bwl_guild.csv
```

## Command Line Options

### Basic Usage
```bash
python raid_attendance_report.py [OPTIONS]
```

### Available Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--raids` | `-r` | Predefined raid set to analyze | `40man_no_ony` |
| `--zones` | `-z` | Specific zone IDs (space-separated) | - |
| `--days` | `-d` | Number of days to analyze | `30` |
| `--output` | `-o` | Output CSV filename | `raid_attendance_report.csv` |
| `--guild-id` | `-g` | Guild ID | `784174` |
| `--guild-members-only` | `-m` | Only include actual guild members | `False` |
| `--list-raids` | `-l` | List all available raids and sets | - |
| `--help` | `-h` | Show help message | - |

### Raid Sets

| Raid Set | Raids Included |
|----------|----------------|
| `40man` | MC, BWL, AQ40, Onyxia |
| `40man_no_ony` | MC, BWL, AQ40 (default) |
| `20man` | ZG, AQ20, Onyxia |
| `mc_only` | Molten Core |
| `bwl_only` | Blackwing Lair |
| `aq40_only` | Temple of Ahn'Qiraj |
| `ony_only` | Onyxia's Lair |
| `zg_only` | Zul'Gurub |
| `aq20_only` | Ruins of Ahn'Qiraj |
| `classic_40man` | MC, BWL, AQ40, Onyxia |
| `all` | All available raids |

### Examples

```bash
# Default report (all players, including PUGs)
python raid_attendance_report.py

# Guild members only (recommended for attendance tracking)
python raid_attendance_report.py --guild-members-only

# Only Molten Core for last 14 days
python raid_attendance_report.py --raids mc_only --days 14

# Custom raid selection by zone IDs
python raid_attendance_report.py --zones 1028 1034 1035

# All 20-man raids with custom output file
python raid_attendance_report.py --raids 20man --output 20man_report.csv

# BWL only for guild members with custom filename
python raid_attendance_report.py --raids bwl_only --guild-members-only --output bwl_guild_attendance.csv

# Last 7 days, all raids, guild members only
python raid_attendance_report.py --days 7 --raids all --guild-members-only

# List all available raid sets and zones
python raid_attendance_report.py --list-raids
```

## Zone IDs (Classic Fresh Anniversary)

| Zone ID | Raid Name |
|---------|-----------|
| 1028 | Molten Core |
| 1034 | Blackwing Lair |
| 1035 | Temple of Ahn'Qiraj (AQ40) |
| 1029 | Onyxia's Lair |
| 1030 | Zul'Gurub |
| 1031 | Ruins of Ahn'Qiraj (AQ20) |

## Configuration

The tool uses `raid_config.py` for configuration:
- Guild ID: 784174 (Well Rested - Nightslayer)
- Default raids: 40-man excluding Onyxia
- Default time period: 30 days

### Environment Variables

The application requires **v2 API credentials** in a `.env` file:

```bash
# Copy the sample file
cp .env.sample .env

# Edit .env with your v2 API credentials
WARCRAFT_LOGS_CLIENT_ID=your_v2_client_id_here
WARCRAFT_LOGS_CLIENT_SECRET=your_v2_client_secret_here
```

**Important**: Get your v2 API credentials from: https://www.warcraftlogs.com/api/clients/
- Make sure to create a **v2 API client** (not v1)
- Choose "Public Client" for the client type
- v1 API credentials will not work with this tool

## Guild Member Filtering

The `--guild-members-only` flag uses the Warcraft Logs Guild Roster API to filter out PUGs and non-guild members:

- **Without flag**: Includes all players who attended raids (guild members + PUGs)
- **With `--guild-members-only`**: Only includes actual guild members

Example results:
- Regular report: ~140 players (includes PUGs)
- Guild members only: ~53 players (guild members only)

This is especially useful for:
- Officer attendance tracking
- Guild performance analysis
- Excluding casual PUG attendees from guild metrics

## Output

Generates CSV files with columns:
- `Player`: Character name
- `Raids_Attended`: Number of raids attended
- `Total_Raids`: Total possible raids in period
- `Attendance_Rate`: Percentage attendance

Players are sorted by attendance rate (highest first).

### Sample Output
```csv
Player,Raids_Attended,Total_Raids,Attendance_Rate
Barbarian,11,11,100.0%
Walintonis,11,11,100.0%
Frylock,11,11,100.0%
Marlton,10,11,90.9%
Steps,10,11,90.9%
```

### Output Differences
- **Regular report**: ~140 players (includes all raid participants)
- **Guild members only**: ~53 players (actual guild members only)

## Troubleshooting

### Common Issues

**Missing API Credentials**
```bash
# Error: No API credentials found
# Solution: Create .env file with your v2 API credentials
cp .env.sample .env
# Edit .env with your Warcraft Logs v2 API credentials from:
# https://www.warcraftlogs.com/api/clients/ (make sure to create v2 client)
```

**Authentication Errors**
```bash
# Error: 401 Unauthorized or authentication failed
# Solution: Verify you have v2 API credentials (not v1)
# v1 credentials will not work with this tool
```

**No Output or Empty Reports**
```bash
# Check if raids exist in the time period
python raid_attendance_report.py --list-raids

# Try a longer time period
python raid_attendance_report.py --days 60

# Check specific raid types
python raid_attendance_report.py --raids all --days 90
```

**Guild Member Filtering Issues**
```bash
# Verify guild roster is accessible
python raid_attendance_report.py --guild-members-only --days 7 --raids mc_only

# Compare with regular report
python raid_attendance_report.py --days 7 --raids mc_only
```

### Getting Help
```bash
# Show all available options
python raid_attendance_report.py --help

# List all raid sets and zone IDs
python raid_attendance_report.py --list-raids
```

## Files

- `raid_attendance_report.py` - Main script with CLI interface
- `raid_config.py` - Configuration and zone definitions  
- `requirements.txt` - Python dependencies
- `.env` - API credentials (create from .env.sample)
- `.env.sample` - Template for environment variables
- `.gitignore` - Git ignore file (excludes .env and sensitive files)
- `tests/` - Test and debug scripts
- `archive/` - Archived/unused files

## API Details

Uses Warcraft Logs Fresh API (https://fresh.warcraftlogs.com/api/v2) with OAuth2 client credentials authentication.

### APIs Used
1. **Attendance API**: Fetches raid attendance data for specified time periods and zones
2. **Guild Roster API**: Fetches current guild member list for filtering PUGs

## Deduplication Logic

If multiple logs exist for the same raid on the same day:
- ✅ Different raids on same day are counted separately (MC + BWL = 2 raids)
- ✅ Multiple logs of same raid are deduplicated (best log with most players is kept)
