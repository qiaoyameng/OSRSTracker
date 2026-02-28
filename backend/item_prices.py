# backend/item_prices.py
import requests
import json
import csv
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# OSRS Wiki API endpoints for item prices
OSRS_WIKI_API_BASE = "https://prices.runescape.wiki/api/v1/osrs"

def get_item_mapping() -> Optional[List[Dict[str, Any]]]:
    """Fetch item mapping from OSRS Wiki API (maps item IDs to names)"""
    url = f"{OSRS_WIKI_API_BASE}/mapping"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching item mapping: {e}")
        return None

def get_latest_prices() -> Optional[Dict[str, Any]]:
    """Fetch latest item prices from OSRS Wiki API"""
    url = f"{OSRS_WIKI_API_BASE}/latest"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest prices: {e}")
        return None

def get_item_timeseries(item_id: int, timestep: str = "5m") -> Optional[Dict[str, Any]]:
    """
    Fetch timeseries data for a specific item
    timestep can be: "5m", "1h", "6h", "24h"
    """
    url = f"{OSRS_WIKI_API_BASE}/timeseries?timestep={timestep}&id={item_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching timeseries for item {item_id}: {e}")
        return None

def search_item_by_name(item_mapping: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Search for items by name (case-insensitive partial match)"""
    query = query.lower()
    matches = []
    
    for item in item_mapping:
        if query in item.get('name', '').lower():
            matches.append(item)
    
    return matches

def get_item_by_id(item_mapping: List[Dict[str, Any]], item_id: int) -> Optional[Dict[str, Any]]:
    """Get item details by ID"""
    for item in item_mapping:
        if item.get('id') == item_id:
            return item
    return None

def format_price(price: int) -> str:
    """Format price with commas and appropriate suffixes (k, m, b)"""
    if price >= 1_000_000_000:
        return f"{price / 1_000_000_000:.2f}b"
    elif price >= 1_000_000:
        return f"{price / 1_000_000:.2f}m"
    elif price >= 1_000:
        return f"{price / 1_000:.2f}k"
    else:
        return f"{price:,}"

def save_item_prices_to_json(prices_data: Dict[str, Any], item_mapping: List[Dict[str, Any]]):
    """Save item prices to JSON file with item names included"""
    # Create data directory if it doesn't exist
    data_dir = 'data/item_prices'
    os.makedirs(data_dir, exist_ok=True)
    
    # Create a lookup dictionary for item names
    item_lookup = {item['id']: item for item in item_mapping}
    
    # Enrich price data with item names
    enriched_data = {
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }
    
    for item_id, price_info in prices_data.get('data', {}).items():
        item_id_int = int(item_id)
        item_info = item_lookup.get(item_id_int, {})
        
        enriched_data['data'][item_id] = {
            'id': item_id_int,
            'name': item_info.get('name', f'Unknown Item {item_id}'),
            'examine': item_info.get('examine', ''),
            'members': item_info.get('members', False),
            'lowalch': item_info.get('lowalch'),
            'highalch': item_info.get('highalch'),
            'limit': item_info.get('limit'),
            'value': item_info.get('value'),
            'high': price_info.get('high'),
            'low': price_info.get('low'),
            'highTime': price_info.get('highTime'),
            'lowTime': price_info.get('lowTime')
        }
    
    # Save to JSON file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_path = f'{data_dir}/item_prices_{timestamp}.json'
    
    with open(json_path, 'w') as json_file:
        json.dump(enriched_data, json_file, indent=4)
    
    # Also save as latest
    latest_path = f'{data_dir}/latest_prices.json'
    with open(latest_path, 'w') as json_file:
        json.dump(enriched_data, json_file, indent=4)
    
    print(f"Item prices saved to {json_path} and {latest_path}")
    return json_path

def save_item_timeseries_to_json(item_id: int, item_name: str, timeseries_data: Dict[str, Any]):
    """Save item timeseries data to JSON file"""
    # Create data directory if it doesn't exist
    data_dir = 'data/item_timeseries'
    os.makedirs(data_dir, exist_ok=True)
    
    # Sanitize item name for filename
    safe_name = item_name.replace(' ', '_').replace("'", '').replace('(', '').replace(')', '').lower()
    
    # Add metadata
    enriched_data = {
        'item_id': item_id,
        'item_name': item_name,
        'timestamp': datetime.now().isoformat(),
        'data': timeseries_data.get('data', [])
    }
    
    # Save to JSON file
    json_path = f'{data_dir}/{safe_name}_{item_id}_timeseries.json'
    
    with open(json_path, 'w') as json_file:
        json.dump(enriched_data, json_file, indent=4)
    
    print(f"Timeseries data saved to {json_path}")
    return json_path

def save_prices_to_csv(prices_data: Dict[str, Any], item_mapping: List[Dict[str, Any]]):
    """Save item prices to CSV file"""
    data_dir = 'data/item_prices'
    os.makedirs(data_dir, exist_ok=True)
    
    # Create a lookup dictionary for item names
    item_lookup = {item['id']: item for item in item_mapping}
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path = f'{data_dir}/item_prices_{timestamp}.csv'
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'high_price', 'low_price', 'high_time', 'low_time', 
                      'members', 'high_alch', 'low_alch', 'buy_limit', 'value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for item_id, price_info in prices_data.get('data', {}).items():
            item_id_int = int(item_id)
            item_info = item_lookup.get(item_id_int, {})
            
            writer.writerow({
                'id': item_id_int,
                'name': item_info.get('name', f'Unknown Item {item_id}'),
                'high_price': price_info.get('high'),
                'low_price': price_info.get('low'),
                'high_time': price_info.get('highTime'),
                'low_time': price_info.get('lowTime'),
                'members': item_info.get('members', False),
                'high_alch': item_info.get('highalch'),
                'low_alch': item_info.get('lowalch'),
                'buy_limit': item_info.get('limit'),
                'value': item_info.get('value')
            })
    
    print(f"CSV data saved to {csv_path}")
    return csv_path

def fetch_all_prices():
    """Main function to fetch all item prices and save them"""
    print("Fetching item mapping...")
    item_mapping = get_item_mapping()
    
    if item_mapping is None:
        print("Failed to fetch item mapping")
        return
    
    print(f"Found {len(item_mapping)} items in mapping")
    
    print("Fetching latest prices...")
    prices_data = get_latest_prices()
    
    if prices_data is None:
        print("Failed to fetch latest prices")
        return
    
    print(f"Found {len(prices_data.get('data', {}))} items with price data")
    
    # Save to JSON and CSV
    json_path = save_item_prices_to_json(prices_data, item_mapping)
    csv_path = save_prices_to_csv(prices_data, item_mapping)
    
    print(f"Successfully saved item prices")
    return json_path, csv_path

def fetch_item_timeseries(item_name_or_id: str, timestep: str = "5m"):
    """Fetch timeseries data for a specific item by name or ID"""
    # First get item mapping
    print("Fetching item mapping...")
    item_mapping = get_item_mapping()
    
    if item_mapping is None:
        print("Failed to fetch item mapping")
        return
    
    # Determine if input is ID or name
    try:
        item_id = int(item_name_or_id)
        item_info = get_item_by_id(item_mapping, item_id)
        if item_info is None:
            print(f"Item with ID {item_id} not found")
            return
        item_name = item_info.get('name', f'Item {item_id}')
    except ValueError:
        # Search by name
        matches = search_item_by_name(item_mapping, item_name_or_id)
        if not matches:
            print(f"No items found matching '{item_name_or_id}'")
            return
        if len(matches) > 1:
            print(f"Found {len(matches)} matches for '{item_name_or_id}':")
            for match in matches[:10]:  # Show first 10 matches
                print(f"  - ID {match['id']}: {match['name']}")
            if len(matches) > 10:
                print(f"  ... and {len(matches) - 10} more")
            return
        
        item_info = matches[0]
        item_id = item_info['id']
        item_name = item_info['name']
    
    print(f"Fetching timeseries for '{item_name}' (ID: {item_id}) with timestep '{timestep}'...")
    timeseries_data = get_item_timeseries(item_id, timestep)
    
    if timeseries_data is None:
        print(f"Failed to fetch timeseries data")
        return
    
    data_points = timeseries_data.get('data', [])
    print(f"Found {len(data_points)} data points")
    
    # Save to JSON
    json_path = save_item_timeseries_to_json(item_id, item_name, timeseries_data)
    
    print(f"Successfully saved timeseries data")
    return json_path

def search_items(query: str):
    """Search for items by name"""
    print(f"Searching for items matching '{query}'...")
    item_mapping = get_item_mapping()
    
    if item_mapping is None:
        print("Failed to fetch item mapping")
        return
    
    matches = search_item_by_name(item_mapping, query)
    
    if not matches:
        print(f"No items found matching '{query}'")
        return
    
    print(f"Found {len(matches)} matches:")
    for match in matches[:20]:  # Show first 20 matches
        members_status = "Members" if match.get('members') else "Free"
        print(f"  ID {match['id']}: {match['name']} ({members_status})")
    
    if len(matches) > 20:
        print(f"  ... and {len(matches) - 20} more")
    
    return matches

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python item_prices.py fetch_all")
        print("  python item_prices.py fetch_timeseries <item_name_or_id> [timestep]")
        print("  python item_prices.py search <query>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'fetch_all':
        fetch_all_prices()
    elif command == 'fetch_timeseries':
        if len(sys.argv) < 3:
            print("Usage: python item_prices.py fetch_timeseries <item_name_or_id> [timestep]")
            sys.exit(1)
        item_name_or_id = sys.argv[2]
        timestep = sys.argv[3] if len(sys.argv) > 3 else "5m"
        fetch_item_timeseries(item_name_or_id, timestep)
    elif command == 'search':
        if len(sys.argv) < 3:
            print("Usage: python item_prices.py search <query>")
            sys.exit(1)
        search_items(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print("Available commands: fetch_all, fetch_timeseries, search")
        sys.exit(1)
