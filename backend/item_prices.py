# backend/item_prices.py
import requests
import json
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

ITEM_PRICES_DIR = os.path.join(os.path.dirname(__file__), 'item_prices')
OSRS_GE_API_BASE = "https://services.runescape.com/m=itemdb_oldschool"
OSRS_GE_DETAIL_API = f"{OSRS_GE_API_BASE}/api/catalogue/detail.json?item="
OSRS_GE_GRAPH_API = f"{OSRS_GE_API_BASE}/api/graph/"

POPULAR_ITEMS = {
    4151: "Abyssal whip",
    4153: "Granite maul",
    6585: "Dragon claws",
    11732: "Dragon boots",
    11802: "Abyssal tentacle",
    11804: "Abyssal bludgeon",
    11806: "Abyssal dagger",
    11808: "Abyssal dagger (p++)",
    12817: "Elysian spirit shield",
    12821: "Arcane spirit shield",
    12829: "Spectral spirit shield",
    12924: "Toxic blowpipe",
    12926: "Toxic staff of the dead",
    12927: "Toxic blowpipe (empty)",
    12931: "Serpentine helm",
    12934: "Zul-andra teleport",
    13239: "Ring of suffering",
    13240: "Ring of suffering (r)",
    13271: "Abyssal dagger (bh)",
    13391: "Twisted bow",
    13441: "Dragon hunter crossbow",
    13576: "Infernal pickaxe",
    13652: "Dragon warhammer",
    19547: "Dragon hunter lance",
    19553: "Necklace of anguish",
    19559: "Tormented bracelet",
    19564: "Tyrannical ring",
    19580: "Ring of suffering (i)",
    19669: "Zulrah's scales",
    21012: "Dexterous prayer scroll",
    21015: "Arcane prayer scroll",
    21021: "Twisted buckler",
    21024: "Dinh's bulwark",
    21028: "Ancestral robe top",
    21030: "Ancestral robe bottom",
    21034: "Dragon harpoon",
    21043: "Dragon sword",
    21060: "Dragon thrownaxe",
    22296: "Scythe of vitur",
    22324: "Sanguinesti staff",
    22326: "Scythe of vitur (uncharged)",
    22328: "Sanguinesti staff (uncharged)",
    22481: "Avernic defender",
    22547: "Dragon crossbow",
    22552: "Dragon javelin",
    23616: "Dragon kiteshield",
    23621: "Dragon platebody",
    2417: "Dragon platelegs",
    2419: "Dragon plateskirt",
    2422: "Dragon full helm",
    2425: "Dragon gauntlets",
    2430: "Dragon boots (g)",
    2434: "Dragon boots (spiked)",
    2438: "Dragon boots (ornate)",
    2440: "Dragon defender",
    2442: "Dragon defender (t)",
    2444: "Dragon defender (l)",
    2446: "Dragon defender (g)",
    2450: "Dragon defender (spiked)",
    2452: "Dragon defender (ornate)",
    11283: "Dragonfire shield",
    11284: "Dragonfire shield (empty)",
    11286: "Dragonfire ward",
    11288: "Dragonfire ward (empty)",
    21793: "Magmum mutagen",
    21795: "Magmum mutagen (uncharged)",
    21797: "Toxic mutagen",
    21799: "Toxic mutagen (uncharged)",
    21807: "Volatile nightmare staff",
    21809: "Volatile nightmare staff (uncharged)",
    21811: "Eldritch nightmare staff",
    21813: "Eldritch nightmare staff (uncharged)",
    21815: "Harmonised nightmare staff",
    21817: "Harmonised nightmare staff (uncharged)",
    22322: "Inquisitor's mace",
    22325: "Inquisitor's armour set",
    22327: "Inquisitor's great helm",
    22329: "Inquisitor's hauberk",
    22331: "Inquisitor's plateskirt",
    22486: "Avernic defender hilt",
    24203: "Tumeken's shadow",
    24205: "Tumeken's shadow (uncharged)",
    24291: "Osmumten's fang",
    25854: "Lightbearer",
    25857: "Elidinis' ward",
    25859: "Elidinis' ward (f)",
    26222: "Masori mask",
    26224: "Masori body",
    26226: "Masori chaps",
    26228: "Masori mask (f)",
    26230: "Masori body (f)",
    26232: "Masori chaps (f)",
    26382: "Torva full helm",
    26384: "Torva platebody",
    26386: "Torva platelegs",
    26703: "Zaryte crossbow",
    27229: "Soulreaper axe",
    27610: "Venator bow",
    27612: "Venator bow (uncharged)",
    27624: "Scorching bow",
    27626: "Scorching bow (uncharged)",
    27633: "Purging staff",
    27635: "Purging staff (uncharged)",
    27657: "Accursed sceptre",
    27659: "Accursed sceptre (u)",
}


def ensure_directory_exists():
    """Create the item prices directory if it doesn't exist."""
    os.makedirs(ITEM_PRICES_DIR, exist_ok=True)


def fetch_item_detail(item_id: int) -> Optional[Dict[str, Any]]:
    """Fetch item detail from OSRS Grand Exchange API."""
    url = f"{OSRS_GE_DETAIL_API}{item_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'item' in data:
            return data['item']
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching detail for item {item_id}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for item {item_id}: {e}")
        return None


def fetch_item_price_history(item_id: int) -> Optional[Dict[str, Any]]:
    """Fetch item price history from OSRS Grand Exchange API."""
    url = f"{OSRS_GE_GRAPH_API}{item_id}.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching price history for item {item_id}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for item {item_id}: {e}")
        return None


def parse_price(price_str: str) -> float:
    """Parse price string like '1.2m' or '500k' to float."""
    if not price_str:
        return 0.0
    
    price_str = str(price_str).replace(',', '').replace(' ', '').lower()
    
    multipliers = {
        'k': 1000,
        'm': 1000000,
        'b': 1000000000
    }
    
    if price_str[-1] in multipliers:
        return float(price_str[:-1]) * multipliers[price_str[-1]]
    
    try:
        return float(price_str)
    except ValueError:
        return 0.0


def parse_price_history(history_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse price history data into a more usable format."""
    daily = history_data.get('daily', {})
    average = history_data.get('average', {})
    
    parsed_daily = []
    for timestamp, price in daily.items():
        date = datetime.fromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d')
        parsed_daily.append({
            'date': date,
            'timestamp': int(timestamp),
            'price': price
        })
    
    parsed_daily.sort(key=lambda x: x['timestamp'])
    
    parsed_average = []
    for timestamp, price in average.items():
        date = datetime.fromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d')
        parsed_average.append({
            'date': date,
            'timestamp': int(timestamp),
            'price': price
        })
    
    parsed_average.sort(key=lambda x: x['timestamp'])
    
    return {
        'daily': parsed_daily,
        'average': parsed_average
    }


def get_item_price_data(item_id: int, item_name: str = None) -> Optional[Dict[str, Any]]:
    """Get complete item price data including current price and history."""
    detail = fetch_item_detail(item_id)
    history = fetch_item_price_history(item_id)
    
    if detail is None:
        return None
    
    item_name = item_name or detail.get('name', f'Item_{item_id}')
    
    current_price = detail.get('current', {})
    today_price = detail.get('today', {})
    day30 = detail.get('day30', {})
    day90 = detail.get('day90', {})
    day180 = detail.get('day180', {})
    
    price_data = {
        'item_id': item_id,
        'item_name': item_name,
        'description': detail.get('description', ''),
        'members': detail.get('members', True),
        'type': detail.get('type', ''),
        'type_icon': detail.get('typeIcon', ''),
        'icon_url': f"{OSRS_GE_API_BASE}/obj_sprite.gif?id={item_id}",
        'large_icon_url': f"{OSRS_GE_API_BASE}/obj_big.gif?id={item_id}",
        'current_price': {
            'price': parse_price(current_price.get('price', '0')),
            'price_str': current_price.get('price', '0'),
            'trend': current_price.get('trend', 'neutral')
        },
        'today': {
            'price': parse_price(today_price.get('price', '0')),
            'price_str': today_price.get('price', '0'),
            'trend': today_price.get('trend', 'neutral')
        },
        'day30': {
            'trend': day30.get('trend', 'neutral'),
            'change': day30.get('change', '0%')
        },
        'day90': {
            'trend': day90.get('trend', 'neutral'),
            'change': day90.get('change', '0%')
        },
        'day180': {
            'trend': day180.get('trend', 'neutral'),
            'change': day180.get('change', '0%')
        },
        'price_history': None,
        'fetched_at': datetime.now().isoformat()
    }
    
    if history:
        price_data['price_history'] = parse_price_history(history)
    
    return price_data


def save_item_price_json(data: Dict[str, Any]) -> str:
    """Save item price data to a JSON file."""
    ensure_directory_exists()
    
    item_id = data['item_id']
    item_name = data['item_name'].replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = f"{item_id}_{item_name}.json"
    filepath = os.path.join(ITEM_PRICES_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Saved price data to: {filepath}")
    return filepath


def get_item_price(item_id: int, item_name: str = None):
    """Fetch and save price data for a single item."""
    print(f"Fetching price data for item ID: {item_id}")
    
    price_data = get_item_price_data(item_id, item_name)
    
    if price_data is None:
        print(f"Failed to fetch price data for item {item_id}")
        return None
    
    save_item_price_json(price_data)
    
    print(f"Successfully processed: {price_data['item_name']}")
    print(f"Current price: {price_data['current_price']['price_str']}")
    
    return price_data


def get_multiple_item_prices(item_ids: List[int] = None, item_names: Dict[int, str] = None):
    """Fetch and save price data for multiple items."""
    if item_ids is None:
        item_ids = list(POPULAR_ITEMS.keys())
    
    if item_names is None:
        item_names = POPULAR_ITEMS
    
    print(f"Fetching price data for {len(item_ids)} items...")
    
    results = []
    for item_id in item_ids:
        item_name = item_names.get(item_id)
        result = get_item_price(item_id, item_name)
        if result:
            results.append(result)
    
    print(f"\nSuccessfully processed {len(results)}/{len(item_ids)} items")
    return results


def get_popular_items_prices():
    """Fetch and save price data for all popular items."""
    print("Fetching prices for popular items...")
    return get_multiple_item_prices()


def list_saved_items() -> List[Dict[str, Any]]:
    """List all saved item price files."""
    ensure_directory_exists()
    
    items = []
    for filename in os.listdir(ITEM_PRICES_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(ITEM_PRICES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                items.append({
                    'item_id': data.get('item_id'),
                    'item_name': data.get('item_name'),
                    'current_price': data.get('current_price', {}).get('price_str', 'N/A'),
                    'fetched_at': data.get('fetched_at'),
                    'filepath': filepath
                })
    
    return items


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python item_prices.py get_item_price <item_id> [item_name]")
        print("  python item_prices.py get_multiple_item_prices <item_id1,item_id2,...>")
        print("  python item_prices.py get_popular_items_prices")
        print("  python item_prices.py list_saved_items")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'get_item_price':
        if len(sys.argv) < 3:
            print("Error: item_id required")
            sys.exit(1)
        item_id = int(sys.argv[2])
        item_name = sys.argv[3] if len(sys.argv) > 3 else None
        get_item_price(item_id, item_name)
    
    elif command == 'get_multiple_item_prices':
        if len(sys.argv) < 3:
            print("Error: comma-separated item_ids required")
            sys.exit(1)
        item_ids = [int(x.strip()) for x in sys.argv[2].split(',')]
        get_multiple_item_prices(item_ids)
    
    elif command == 'get_popular_items_prices':
        get_popular_items_prices()
    
    elif command == 'list_saved_items':
        items = list_saved_items()
        for item in items:
            print(f"  {item['item_id']}: {item['item_name']} - {item['current_price']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
