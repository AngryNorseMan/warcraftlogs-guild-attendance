#!/usr/bin/env python3
"""
Guild Raid Attendance Report Generator
Fetches raid attendance data from Warcraft Logs API and generates a CSV report
for 40-man raids (excluding AQ20, ZG, and Onyxia) for the last 30 days.
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from collections import defaultdict
import sys
import os
import base64
import argparse
from dotenv import load_dotenv
from raid_config import ALL_RAIDS, RAID_SETS, CURRENT_CONFIG

# Load environment variables
load_dotenv()

# Configuration - loaded from config file and command line
GUILD_ID = CURRENT_CONFIG["guild_id"]
DAYS_TO_ANALYZE = CURRENT_CONFIG["days_to_analyze"]
OUTPUT_FILE = CURRENT_CONFIG["output_file"]

# Warcraft Logs API configuration - loaded from environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
BASE_URL = "https://fresh.warcraftlogs.com/api/v2"  # Using Fresh for Classic Anniversary
AUTH_URL = "https://fresh.warcraftlogs.com/oauth/token"

# Validate required environment variables
if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ Error: CLIENT_ID and CLIENT_SECRET must be set in .env file")
    print("📝 Please copy .env.sample to .env and add your Warcraft Logs API credentials")
    print("🔗 Get credentials from: https://www.warcraftlogs.com/api/clients/")
    sys.exit(1)

# Remove the hardcoded raid definitions since we're using the config file now

class WarcraftLogsAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.base_url = BASE_URL
        self.auth_url = AUTH_URL
        
    def authenticate(self):
        """Authenticate with Warcraft Logs API and get access token"""
        print("🔐 Starting authentication...")
        
        # Create basic auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        try:
            print(f"Making request to: {self.auth_url}")
            response = requests.post(self.auth_url, headers=headers, data=data, timeout=30)
            print(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            if not self.access_token:
                print(f"Token response: {token_data}")
                raise ValueError("No access token received")
                
            print("✓ Successfully authenticated with Warcraft Logs API")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Authentication failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during authentication: {e}")
            return False
    
    def get_headers(self):
        """Get headers with authorization token"""
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def execute_query(self, query, variables=None):
        """Execute a GraphQL query"""
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            print("🔍 Executing GraphQL query...")
            response = requests.post(
                f"{self.base_url}/client",
                headers=self.get_headers(),
                json=payload,
                timeout=60
            )
            print(f"Query response status: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            if 'errors' in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return None
            
            print("✓ GraphQL query executed successfully")
            return data.get('data')
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to execute query: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error during query execution: {e}")
            return None
    
    def get_guild_attendance(self, guild_id, page=1):
        """Get guild attendance data using the attendance API endpoint"""
        query = """
        query($guildID: Int!, $page: Int!) {
          guildData {
            guild(id: $guildID) {
              name
              server {
                name
                region {
                  name
                }
              }
              attendance(page: $page) {
                data {
                  zone {
                    id
                    name
                  }
                  code
                  startTime
                  players {
                    name
                    type
                  }
                }
                has_more_pages
                current_page
                total
              }
            }
          }
        }
        """
        
        variables = {
            'guildID': guild_id,
            'page': page
        }
        
        print(f"🔍 Fetching attendance data for guild ID: {guild_id} (page {page})")
        data = self.execute_query(query, variables)
        
        if data and data.get('guildData') and data['guildData'].get('guild'):
            guild_info = data['guildData']['guild']
            guild_name = guild_info.get('name', 'Unknown')
            server_info = guild_info.get('server', {})
            server_name = server_info.get('name', 'Unknown')
            region_name = server_info.get('region', {}).get('name', 'Unknown')
            
            print(f"✓ Found guild: {guild_name} on {server_name}-{region_name}")
            
            attendance_data = guild_info.get('attendance', {})
            raids = attendance_data.get('data', [])
            has_more = attendance_data.get('has_more_pages', False)
            total_raids = attendance_data.get('total', 0)
            
            print(f"✓ Found {len(raids)} raids on this page (Total: {total_raids})")
            return raids, has_more
        else:
            print("❌ No attendance data found or guild not found")
            return [], False

    def get_guild_roster(self, guild_id):
        """Get the current guild roster to filter attendance to only guild members"""
        query = """
        query($guildID: Int!) {
          guildData {
            guild(id: $guildID) {
              name
              members {
                data {
                  name
                  level
                  classID
                }
              }
            }
          }
        }
        """
        
        variables = {
            'guildID': guild_id
        }
        
        print(f"👥 Fetching guild roster for guild ID: {guild_id}")
        data = self.execute_query(query, variables)
        
        if data and data.get('guildData') and data['guildData'].get('guild'):
            guild_info = data['guildData']['guild']
            guild_name = guild_info.get('name', 'Unknown')
            
            members_data = guild_info.get('members', {})
            members = members_data.get('data', [])
            
            print(f"✓ Found {len(members)} guild members in {guild_name}")
            
            # Extract just the member names for filtering
            member_names = set()
            for member in members:
                name = member.get('name', '')
                if name:
                    member_names.add(name)
            
            print(f"✓ Guild member names extracted: {len(member_names)} members")
            return member_names
        else:
            print("❌ No guild roster data found")
            return set()

    def get_all_guild_attendance(self, guild_id, days=30):
        """Get all guild attendance data for the specified time period"""
        all_raids = []
        page = 1
        has_more = True
        cutoff_date = datetime.now() - timedelta(days=days)
        
        print(f"📅 Getting raids from the last {days} days (since {cutoff_date.strftime('%Y-%m-%d')})")
        
        while has_more:
            raids, has_more = self.get_guild_attendance(guild_id, page)
            
            for raid in raids:
                # Check if raid is within our date range
                start_time = raid.get('startTime', 0)
                if start_time:
                    raid_date = datetime.fromtimestamp(start_time / 1000)
                    if raid_date < cutoff_date:
                        print(f"⏰ Reached raids older than {days} days, stopping")
                        has_more = False
                        break
                
                all_raids.append(raid)
            
            if has_more:
                page += 1
                print(f"📄 Fetching page {page}...")
        
        print(f"✅ Collected {len(all_raids)} raids total")
        return all_raids

    def get_guild_reports(self, guild_name, server_name, region="US", days=30):
        """Fetch guild reports for the last N days"""
        # Calculate timestamps (Warcraft Logs uses Unix timestamps in milliseconds)
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        query = """
        query($guildName: String!, $serverName: String!, $serverRegion: String!, $startTime: Float!, $endTime: Float!) {
          guild(name: $guildName, serverName: $serverName, serverRegion: $serverRegion) {
            name
            reports(startTime: $startTime, endTime: $endTime, limit: 100) {
              data {
                code
                title
                startTime
                endTime
                zone {
                  id
                  name
                }
                fights {
                  id
                  encounterID
                  name
                  startTime
                  endTime
                  kill
                  difficulty
                }
              }
            }
          }
        }
        """
        
        variables = {
            'guildName': guild_name,
            'serverName': server_name,
            'serverRegion': region,
            'startTime': start_time,
            'endTime': end_time
        }
        
        print(f"🔍 Searching for guild: {guild_name} on {server_name}-{region}")
        data = self.execute_query(query, variables)
        if data and data.get('guild') and data['guild'].get('reports'):
            reports = data['guild']['reports']['data']
            print(f"✓ Fetched {len(reports)} reports from the last {days} days")
            return reports
        else:
            print("❌ No reports found or guild not found")
            print("   Please check your guild name, server name, and region")
            return []
    
    def get_report_attendance(self, report_code, fight_id):
        """Get attendance data for a specific fight in a report"""
        query = """
        query($reportCode: String!, $fightID: Int!) {
          reportData {
            report(code: $reportCode) {
              fights(fightIDs: [$fightID]) {
                id
                name
                startTime
                endTime
                playerDetails {
                  data {
                    players {
                      name
                      id
                      type
                      server
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        variables = {
            'reportCode': report_code,
            'fightID': fight_id
        }
        
        data = self.execute_query(query, variables)
        if data and data.get('reportData') and data['reportData'].get('report'):
            fights = data['reportData']['report'].get('fights', [])
            if fights:
                return fights[0].get('playerDetails', {}).get('data', {}).get('players', [])
        
        return []

def is_included_raid(zone_id, included_raids):
    """Check if a raid is in the included raids list"""
    return zone_id in included_raids

def process_attendance_data_v2(api, guild_id, days=30, included_raids=None, guild_members_only=False):
    """Process raid attendance data using the attendance API endpoint"""
    if included_raids is None:
        included_raids = CURRENT_CONFIG["included_raids"]
    
    print("📊 Processing raid attendance data (v2 - using attendance API)...")
    print(f"🎯 Including raids: {[ALL_RAIDS.get(rid, f'Unknown-{rid}') for rid in included_raids]}")
    
    # Get guild roster if filtering to members only
    guild_members = set()
    if guild_members_only:
        guild_members = api.get_guild_roster(guild_id)
        if not guild_members:
            print("⚠️  Warning: Could not fetch guild roster, proceeding with all players")
            guild_members_only = False
        else:
            print(f"👥 Will filter to {len(guild_members)} guild members only")
    
    # Get all attendance data
    all_raids = api.get_all_guild_attendance(guild_id, days)
    
    if not all_raids:
        print("❌ No attendance data found")
        return None
    
    # Group raids by date and zone to avoid counting multiple logs of the same raid
    unique_raids = {}
    
    print(f"🔍 Filtering and deduplicating raids...")
    
    for raid in all_raids:
        zone = raid.get('zone', {})
        zone_id = zone.get('id')
        zone_name = zone.get('name', 'Unknown')
        
        # Skip if not in our included raids list
        if not is_included_raid(zone_id, included_raids):
            print(f"  ⏭️  Skipping {zone_name} (not in included list)")
            continue
        
        # Get raid date
        start_time = raid.get('startTime', 0)
        if start_time:
            raid_date = datetime.fromtimestamp(start_time / 1000).strftime('%Y-%m-%d')
        else:
            raid_date = 'unknown'
        
        # Create unique key based on date and zone
        unique_key = f"{raid_date}_{zone_id}"
        
        # Keep the raid with the most players (best log)
        players = raid.get('players', [])
        player_count = len([p for p in players if p.get('type') == 'Player'])
        
        if unique_key not in unique_raids or player_count > unique_raids[unique_key]['player_count']:
            unique_raids[unique_key] = {
                'raid': raid,
                'player_count': player_count,
                'zone_name': zone_name,
                'date': raid_date,
                'report_code': raid.get('code', 'Unknown')
            }
            print(f"  ✅ Updated best log for {zone_name} ({raid_date}): {player_count} players - {raid.get('code', 'Unknown')}")
        else:
            print(f"  🔄 Skipping duplicate {zone_name} ({raid_date}): {player_count} players (keeping better log)")
    
    if not unique_raids:
        print("❌ No valid raids found matching the specified criteria")
        return None
    
    print(f"\n📋 Processing {len(unique_raids)} unique raid instances:")
    
    # Process unique raids for attendance
    player_attendance = defaultdict(lambda: {'attended': 0, 'total_raids': 0})
    raid_dates = []
    
    for unique_key, raid_info in unique_raids.items():
        raid = raid_info['raid']
        zone_name = raid_info['zone_name']
        raid_date = raid_info['date']
        report_code = raid_info['report_code']
        
        print(f"  📊 {zone_name} ({raid_date}) - {report_code}")
        
        raid_dates.append(raid_date)
        
        # Process players in this raid
        players = raid.get('players', [])
        
        # Debug: Let's see the structure of the players data
        if players:
            print(f"    🔍 Sample player data: {players[0]}")
        
        raid_players = []
        guild_only_players = []
        
        for player in players:
            player_name = player.get('name', '')
            player_type = player.get('type', '')
            
            # In the attendance API, 'type' is actually the player's class
            # All entries should be actual players, so we just need to check for valid name and type
            if player_name and player_type:
                raid_players.append(player_name)
                
                # If filtering to guild members only, check if player is in guild
                if guild_members_only:
                    if player_name in guild_members:
                        guild_only_players.append(player_name)
                        player_attendance[player_name]['attended'] += 1
                else:
                    player_attendance[player_name]['attended'] += 1
        
        if guild_members_only:
            print(f"    👥 {len(raid_players)} total players attended, {len(guild_only_players)} guild members")
            if guild_only_players:
                print(f"    📝 Guild members: {guild_only_players[:5]}{'...' if len(guild_only_players) > 5 else ''}")
        else:
            print(f"    👥 {len(raid_players)} unique players attended")
            if raid_players:
                print(f"    📝 Sample players: {raid_players[:5]}{'...' if len(raid_players) > 5 else ''}")
    
    valid_raids = len(unique_raids)
    
    if not player_attendance:
        print("❌ No player attendance data found")
        if guild_members_only:
            print("🔍 This might indicate that no guild members attended the selected raids")
        else:
            print("🔍 This might indicate an issue with the attendance data structure")
        return None
    
    # Set total possible raids for all players who attended at least one raid
    for player_name in player_attendance:
        player_attendance[player_name]['total_raids'] = valid_raids
    
    filter_msg = " (guild members only)" if guild_members_only else ""
    print(f"✅ Processed {valid_raids} unique raid instances")
    print(f"✅ Found {len(player_attendance)} unique players{filter_msg}")
    
    return player_attendance, raid_dates

def generate_csv_report(player_attendance, raid_dates, output_file="raid_attendance_report.csv"):
    """Generate CSV report with attendance data"""
    print(f"📝 Generating CSV report: {output_file}")
    
    # Prepare data for CSV
    report_data = []
    
    for player_name, stats in player_attendance.items():
        if stats['total_raids'] > 0:
            attendance_rate = (stats['attended'] / stats['total_raids']) * 100
            
            report_data.append({
                'Player': player_name,
                'Raids_Attended': stats['attended'],
                'Total_Raids': stats['total_raids'],
                'Attendance_Rate': f"{attendance_rate:.1f}%",
                'Attendance_Decimal': attendance_rate
            })
    
    # Sort by attendance rate (highest to lowest)
    report_data.sort(key=lambda x: x['Attendance_Decimal'], reverse=True)
    
    # Remove the decimal column used for sorting
    for row in report_data:
        del row['Attendance_Decimal']
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(report_data)
    df.to_csv(output_file, index=False)
    
    print(f"✓ Report saved to {output_file}")
    print(f"✓ Total players: {len(report_data)}")
    
    if raid_dates:
        print(f"✓ Date range: {min(raid_dates)} to {max(raid_dates)}")
    
    # Display top 10 players
    print("\n🏆 Top 10 Raiders by Attendance:")
    print("-" * 50)
    for i, row in enumerate(df.head(10).itertuples(index=False), 1):
        print(f"{i:2d}. {row.Player:<15} {row.Attendance_Rate:>6} ({row.Raids_Attended}/{row.Total_Raids})")
    
    return df

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate guild raid attendance report from Warcraft Logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default 40-man raids (no Onyxia)
  python raid_attendance_report.py
  
  # Only Molten Core
  python raid_attendance_report.py --raids mc_only
  
  # Custom raid list by zone IDs
  python raid_attendance_report.py --zones 1000 1002
  
  # All 20-man raids
  python raid_attendance_report.py --raids 20man
  
  # Custom time period
  python raid_attendance_report.py --days 14
  
  # Custom output file
  python raid_attendance_report.py --output my_report.csv
  
  # Guild members only (exclude PUGs)
  python raid_attendance_report.py --guild-members-only

Available raid sets: """ + ", ".join(RAID_SETS.keys()) + """

Available raids:""" + "\n".join([f"  {zone_id}: {name}" for zone_id, name in ALL_RAIDS.items()])
    )
    
    parser.add_argument(
        '--raids', '-r',
        choices=list(RAID_SETS.keys()),
        help='Predefined raid set to analyze'
    )
    
    parser.add_argument(
        '--zones', '-z',
        type=int,
        nargs='+',
        help='Specific zone IDs to analyze (space-separated)'
    )
    
    parser.add_argument(
        '--days', '-d',
        type=int,
        default=CURRENT_CONFIG["days_to_analyze"],
        help=f'Number of days to analyze (default: {CURRENT_CONFIG["days_to_analyze"]})'
    )
    
    parser.add_argument(
        '--output', '-o',
        default=CURRENT_CONFIG["output_file"],
        help=f'Output CSV filename (default: {CURRENT_CONFIG["output_file"]})'
    )
    
    parser.add_argument(
        '--guild-id', '-g',
        type=int,
        default=CURRENT_CONFIG["guild_id"],
        help=f'Guild ID (default: {CURRENT_CONFIG["guild_id"]})'
    )
    
    parser.add_argument(
        '--guild-members-only', '-m',
        action='store_true',
        help='Only include actual guild members (excludes PUGs and non-guild players)'
    )
    
    parser.add_argument(
        '--list-raids', '-l',
        action='store_true',
        help='List all available raids and raid sets'
    )
    
    return parser.parse_args()

def list_available_raids():
    """Display all available raids and raid sets"""
    print("🎮 Available Raids:")
    print("=" * 50)
    for zone_id, name in ALL_RAIDS.items():
        print(f"  {zone_id:4d}: {name}")
    
    print("\n📋 Available Raid Sets:")
    print("=" * 50)
    for set_name, zone_ids in RAID_SETS.items():
        raid_names = [ALL_RAIDS.get(zid, f"Unknown-{zid}") for zid in zone_ids]
        print(f"  {set_name}:")
        for name in raid_names:
            print(f"    - {name}")
        print()

def main():
    """Main function to run the attendance report generator"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Handle list raids option
    if args.list_raids:
        list_available_raids()
        return
    
    # Determine which raids to include
    if args.zones:
        included_raids = args.zones
        raid_source = f"Custom zones: {args.zones}"
    elif args.raids:
        included_raids = RAID_SETS[args.raids]
        raid_source = f"Raid set: {args.raids}"
    else:
        included_raids = CURRENT_CONFIG["included_raids"]
        raid_source = "Default configuration"
    
    # Validate zone IDs
    invalid_zones = [zid for zid in included_raids if zid not in ALL_RAIDS]
    if invalid_zones:
        print(f"❌ Invalid zone IDs: {invalid_zones}")
        print("Use --list-raids to see available zones")
        sys.exit(1)
    
    print("🎮 Guild Raid Attendance Report Generator")
    print("=" * 50)
    print(f"Guild ID: {args.guild_id}")
    print(f"Analyzing last {args.days} days")
    print(f"Raid selection: {raid_source}")
    print(f"Filter mode: {'Guild members only' if args.guild_members_only else 'All players (including PUGs)'}")
    
    # Show included raids
    included_raid_names = [ALL_RAIDS[zid] for zid in included_raids]
    print(f"Including raids:")
    for name in included_raid_names:
        print(f"  - {name}")
    
    print(f"Output file: {args.output}")
    print("-" * 50)
    
    # Initialize API client
    api = WarcraftLogsAPI(CLIENT_ID, CLIENT_SECRET)
    
    # Authenticate
    if not api.authenticate():
        sys.exit(1)
    
    # Process attendance data using the new attendance API
    result = process_attendance_data_v2(api, args.guild_id, args.days, included_raids, args.guild_members_only)
    
    if result is None:
        print("❌ Failed to process attendance data")
        sys.exit(1)
    
    player_attendance, raid_dates = result
    
    # Generate CSV report
    df = generate_csv_report(player_attendance, raid_dates, args.output)
    
    print("\n✅ Attendance report generation completed!")

if __name__ == "__main__":
    main()
