# backend/player_info.py
import requests
import json
import csv
import sys
import os
import re
from typing import Dict, Any, Optional

def parse_hiscores_data(data: str) -> Dict[str, Any]:
    """Parse the CSV-like hiscores data from OSRS API"""
    lines = data.strip().split('\n')
    
    # Skill names in order as returned by the API
    skills = [
        'overall', 'attack', 'defence', 'strength', 'hitpoints', 
        'ranged', 'prayer', 'magic', 'cooking', 'woodcutting', 
        'fletching', 'fishing', 'firemaking', 'crafting', 'smithing',
        'mining', 'herblore', 'agility', 'thieving', 'slayer', 
        'farming', 'runecrafting', 'hunter', 'construction'
    ]
    
    # Activities/minigames in order
    activities = [
        'league_points', 'bounty_hunter_hunter', 'bounty_hunter_rogue',
        'bounty_hunter_hunter_legacy', 'bounty_hunter_rogue_legacy',
        'clue_scrolls_all', 'clue_scrolls_beginner', 'clue_scrolls_easy',
        'clue_scrolls_medium', 'clue_scrolls_hard', 'clue_scrolls_elite',
        'clue_scrolls_master', 'lms_rank', 'pvp_arena_rank', 'soul_wars_zeal',
        'rifts_closed', 'colosseum_glory'
    ]
    
    # Boss names in order (this is a subset - the full list is quite long)
    bosses = [
        'abyssal_sire', 'alchemical_hydra', 'artio', 'barrows_chests',
        'bryophyta', 'callisto', 'calvarion', 'cerberus', 'chambers_of_xeric',
        'chambers_of_xeric_challenge_mode', 'chaos_elemental', 'chaos_fanatic',
        'commander_zilyana', 'corporeal_beast', 'crazy_archaeologist',
        'dagannoth_prime', 'dagannoth_rex', 'dagannoth_supreme',
        'deranged_archaeologist', 'duke_sucellus', 'general_graardor',
        'giant_mole', 'grotesque_guardians', 'hespori', 'kalphite_queen',
        'king_black_dragon', 'kraken', 'kreearra', 'kril_tsutsaroth',
        'mimic', 'nex', 'nightmare', 'phosanis_nightmare', 'obor',
        'phantom_muspah', 'sarachnis', 'scorpia', 'skotizo', 'spindel',
        'tempoross', 'the_gauntlet', 'the_corrupted_gauntlet', 'the_leviathan',
        'the_whisperer', 'theatre_of_blood', 'theatre_of_blood_hard_mode',
        'thermonuclear_smoke_devil', 'tombs_of_amascut', 'tombs_of_amascut_expert',
        'tzkal_zuk', 'tztok_jad', 'vardorvis', 'venenatis', 'vetion',
        'vorkath', 'wintertodt', 'zalcano', 'zulrah'
    ]
    
    parsed_data = {
        'skills': {},
        'activities': {},
        'bosses': {}
    }
    
    line_index = 0
    
    # Parse skills (first 24 lines)
    for i, skill in enumerate(skills):
        if line_index < len(lines):
            parts = lines[line_index].split(',')
            if len(parts) >= 3:
                rank = int(parts[0]) if parts[0] != '-1' else -1
                level = int(parts[1]) if parts[1] != '-1' else 1
                xp = int(parts[2]) if parts[2] != '-1' else 0
                
                parsed_data['skills'][skill] = {
                    'skill_name': skill.replace('_', ' ').title(),
                    'rank': rank,
                    'level': level,
                    'xp': xp
                }
            line_index += 1
    
    # Parse activities
    for activity in activities:
        if line_index < len(lines):
            parts = lines[line_index].split(',')
            if len(parts) >= 2:
                rank = int(parts[0]) if parts[0] != '-1' else -1
                score = int(parts[1]) if parts[1] != '-1' else 0
                
                parsed_data['activities'][activity] = {
                    'activity_name': activity.replace('_', ' ').title(),
                    'rank': rank,
                    'score': score
                }
            line_index += 1
    
    # Parse bosses
    for boss in bosses:
        if line_index < len(lines):
            parts = lines[line_index].split(',')
            if len(parts) >= 2:
                rank = int(parts[0]) if parts[0] != '-1' else -1
                kills = int(parts[1]) if parts[1] != '-1' else 0
                
                parsed_data['bosses'][boss] = {
                    'boss_name': boss.replace('_', ' ').title(),
                    'rank': rank,
                    'kills': kills
                }
            line_index += 1
    
    return parsed_data

def validate_username(username: str) -> bool:
    """Validate username format."""

    # Check that the username exists.
    if not username:
        return False
    
    # Check that the length of the username is acceptable.
    if len(username) < 1 or len(username) > 12:
        return False

    # Check for acceptable characters.
    if not re.match(r'^[a-zA-Z0-9 _-]+$', username):
        return False

    return True

def sanitize_username(username: str) -> str:
    """Sanitize username format."""

    # Subsitute spaces with underscores.
    return re.sub(r'[^a-zA-Z0-9 _-]', '_', username)

def get_player_data(username: str) -> Optional[Dict[str, Any]]:
    """Fetch player data from official OSRS API"""
    url = f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={username}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            return parse_hiscores_data(response.text)
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {username}: {e}")
        return None

def save_to_json(data: Dict[str, Any], username: str):
    """Save data to JSON file"""
    # Save skill stats (for backward compatibility)
    username = sanitize_username(username)
    skill_stats_path = 'backend/skill_stats.json'
    with open(skill_stats_path, 'w') as json_file:
        json.dump(data['skills'], json_file, indent=4)
    
    # Save complete player data
    complete_data = {
        'username': username,
        'skills': data['skills'],
        'activities': data['activities'],
        'bosses': data['bosses']
    }
    
    complete_data_path = f'backend/{username}_complete_data.json'
    with open(complete_data_path, 'w') as json_file:
        json.dump(complete_data, json_file, indent=4)
    
    print(f"JSON data saved to {skill_stats_path} and {complete_data_path}")

def save_to_csv(data: Dict[str, Any], username: str):
    """Save data to CSV files"""
    # Create backend directory if it doesn't exist
    os.makedirs('backend', exist_ok=True)
    
    # Save skills to CSV
    username = sanitize_username(username)
    skills_csv_path = f'backend/{username}_skills.csv'
    with open(skills_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['skill_name', 'rank', 'level', 'xp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for skill_data in data['skills'].values():
            writer.writerow(skill_data)
    
    # Save activities to CSV
    activities_csv_path = f'backend/{username}_activities.csv'
    with open(activities_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['activity_name', 'rank', 'score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for activity_data in data['activities'].values():
            writer.writerow(activity_data)
    
    # Save bosses to CSV
    bosses_csv_path = f'backend/{username}_bosses.csv'
    with open(bosses_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['boss_name', 'rank', 'kills']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for boss_data in data['bosses'].values():
            writer.writerow(boss_data)
    
    print(f"CSV data saved to {skills_csv_path}, {activities_csv_path}, and {bosses_csv_path}")

def get_skills(username: str):
    """Main function to get all player data"""
    # Validate username
    if not validate_username(username):
        print(f"Error. Invalid username format. Must be between 1 and 12 characters and only alphanumeric characters or dashes, underscores, and spaces.")
        return

    print(f"Fetching data for player: {username}")
    
    player_data = get_player_data(username)
    
    if player_data is None:
        print(f"Failed to fetch data for {username}")
        return
    
    # Save to both JSON and CSV formats
    save_to_json(player_data, username)
    save_to_csv(player_data, username)
    
    print(f"Successfully processed data for {username}")
    print(f"Skills found: {len(player_data['skills'])}")
    print(f"Activities found: {len(player_data['activities'])}")
    print(f"Bosses found: {len(player_data['bosses'])}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python player_info.py get_skills <username>")
        sys.exit(1)
    
    globals()[sys.argv[1]](sys.argv[2])