# backend/item_prices.py
import requests
import json
import os
from typing import Dict, Any, Optional

def get_item_prices(item_id: int) -> Optional[Dict[str, Any]]:
    """Fetch item price data from OSRS API"""
    url = f"https://prices.runescape.wiki/api/v1/osrs/latest?id={item_id}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for item {item_id}: {e}")
        return None

def get_item_history(item_id: int, timestep: str = "1h") -> Optional[Dict[str, Any]]:
    """Fetch item price history from OSRS API"""
    url = f"https://prices.runescape.wiki/api/v1/osrs/history?timestep={timestep}&id={item_id}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching history for item {item_id}: {e}")
        return None

def save_item_data_to_json(data: Dict[str, Any], item_id: int, directory: str = "backend/item_prices_json"):
    """Save item price data to JSON file"""
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Save item data
    file_path = os.path.join(directory, f"item_{item_id}_prices.json")
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"JSON data saved to {file_path}")

def save_item_history_to_json(data: Dict[str, Any], item_id: int, directory: str = "backend/item_prices_json"):
    """Save item price history to JSON file"""
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Save item history
    file_path = os.path.join(directory, f"item_{item_id}_history.json")
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"JSON history saved to {file_path}")

def get_item_name(item_id: int) -> Optional[str]:
    """Get item name from OSRS API"""
    url = f"https://prices.runescape.wiki/api/v1/osrs/mapping"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            mapping = response.json()
            for item in mapping:
                if item['id'] == item_id:
                    return item['name']
            return None
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching item mapping: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    item_id = 4151  # Abyssal whip
    
    # Get item prices
    item_prices = get_item_prices(item_id)
    if item_prices:
        save_item_data_to_json(item_prices, item_id)
    
    # Get item history
    item_history = get_item_history(item_id)
    if item_history:
        save_item_history_to_json(item_history, item_id)
    
    # Get item name
    item_name = get_item_name(item_id)
    if item_name:
        print(f"Item name: {item_name}")