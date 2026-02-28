# backend/item_trends_graphs.py
import json
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import from item_prices module
from item_prices import get_item_timeseries, get_item_mapping, get_item_by_id, search_item_by_name

def load_timeseries_data(json_path: str) -> Optional[Dict[str, Any]]:
    """Load timeseries data from a JSON file"""
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {json_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def format_timestamp(ts: int) -> str:
    """Format Unix timestamp to readable date string"""
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

def format_price(price: Optional[int]) -> str:
    """Format price with appropriate suffixes (k, m, b)"""
    if price is None:
        return "N/A"
    if price >= 1_000_000_000:
        return f"{price / 1_000_000_000:.2f}b"
    elif price >= 1_000_000:
        return f"{price / 1_000_000:.2f}m"
    elif price >= 1_000:
        return f"{price / 1_000:.2f}k"
    else:
        return f"{price:,}"

def create_price_trend_graph(timeseries_data: Dict[str, Any], output_path: str) -> str:
    """
    Create a Plotly graph showing price trends for an item.
    Saves as both HTML (interactive) and PNG (static image).
    """
    item_name = timeseries_data.get('item_name', 'Unknown Item')
    item_id = timeseries_data.get('item_id', 0)
    data_points = timeseries_data.get('data', [])
    
    if not data_points:
        print(f"No data points available for {item_name}")
        return ""
    
    # Extract data
    timestamps = []
    avg_high_prices = []
    avg_low_prices = []
    high_prices = []
    low_prices = []
    
    for point in data_points:
        ts = point.get('timestamp')
        if ts:
            timestamps.append(datetime.fromtimestamp(ts))
            avg_high_prices.append(point.get('avgHighPrice'))
            avg_low_prices.append(point.get('avgLowPrice'))
            high_prices.append(point.get('highPrice'))
            low_prices.append(point.get('lowPrice'))
    
    # Create figure with secondary y-axis for volume
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{item_name} Price Trends', 'Volume'),
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    # Add price traces
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=avg_high_prices,
            name='Avg High Price',
            line=dict(color='#2ecc71', width=2),
            mode='lines',
            hovertemplate='%{y:,.0f} gp<extra>Avg High</extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=avg_low_prices,
            name='Avg Low Price',
            line=dict(color='#e74c3c', width=2),
            mode='lines',
            hovertemplate='%{y:,.0f} gp<extra>Avg Low</extra>'
        ),
        row=1, col=1
    )
    
    # Add high/low price range as filled area
    fig.add_trace(
        go.Scatter(
            x=timestamps + timestamps[::-1],
            y=high_prices + low_prices[::-1],
            fill='toself',
            fillcolor='rgba(52, 152, 219, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Price Range',
            hoverinfo='skip',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Add volume bars
    volumes = [point.get('highPriceVolume', 0) + point.get('lowPriceVolume', 0) for point in data_points]
    fig.add_trace(
        go.Bar(
            x=timestamps,
            y=volumes,
            name='Volume',
            marker_color='rgba(52, 152, 219, 0.6)',
            hovertemplate='%{y:,.0f}<extra>Volume</extra>'
        ),
        row=2, col=1
    )
    
    # Calculate price change statistics
    if avg_high_prices and avg_low_prices:
        first_high = next((p for p in avg_high_prices if p is not None), None)
        last_high = next((p for p in reversed(avg_high_prices) if p is not None), None)
        first_low = next((p for p in avg_low_prices if p is not None), None)
        last_low = next((p for p in reversed(avg_low_prices) if p is not None), None)
        
        if first_high and last_high:
            high_change = ((last_high - first_high) / first_high) * 100
        else:
            high_change = 0
            
        if first_low and last_low:
            low_change = ((last_low - first_low) / first_low) * 100
        else:
            low_change = 0
    else:
        high_change = 0
        low_change = 0
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'{item_name} (ID: {item_id}) - Price Trend Analysis',
            x=0.5,
            font=dict(size=20)
        ),
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=800,
        margin=dict(l=60, r=40, t=120, b=60)
    )
    
    # Update y-axes
    fig.update_yaxes(
        title_text="Price (gp)",
        tickformat=",",
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Volume",
        tickformat=",",
        row=2, col=1
    )
    fig.update_xaxes(title_text="Date/Time", row=2, col=1)
    
    # Add annotations for price changes
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"High Price Change: {high_change:+.2f}%<br>Low Price Change: {low_change:+.2f}%",
        showarrow=False,
        font=dict(size=12),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="rgba(0, 0, 0, 0.2)",
        borderwidth=1,
        borderpad=4,
        align="left",
        valign="top"
    )
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save as HTML (interactive)
    html_path = output_path.replace('.png', '.html')
    fig.write_html(html_path, include_plotlyjs='cdn')
    print(f"Interactive graph saved to {html_path}")
    
    # Try to save as PNG (static image) - requires kaleido
    try:
        fig.write_image(output_path, width=1200, height=800, scale=2)
        print(f"Static image saved to {output_path}")
    except Exception as e:
        print(f"Note: Could not save PNG image (kaleido may not be properly installed): {e}")
        print(f"The interactive HTML graph is still available at {html_path}")
    
    return html_path

def generate_graph_from_file(json_path: str, output_dir: str = 'data/item_trend_graphs') -> str:
    """Generate a trend graph from a timeseries JSON file"""
    # Load data
    timeseries_data = load_timeseries_data(json_path)
    if timeseries_data is None:
        return ""
    
    item_name = timeseries_data.get('item_name', 'unknown_item')
    item_id = timeseries_data.get('item_id', 0)
    
    # Sanitize item name for filename
    safe_name = item_name.replace(' ', '_').replace("'", '').replace('(', '').replace(')', '').lower()
    
    # Create output path
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'{output_dir}/{safe_name}_{item_id}_trend_{timestamp}.png'
    
    # Create graph
    return create_price_trend_graph(timeseries_data, output_path)

def generate_graph_for_item(item_name_or_id: str, timestep: str = "5m", 
                            output_dir: str = 'data/item_trend_graphs') -> str:
    """
    Fetch timeseries data for an item and generate a trend graph.
    """
    # First get item mapping
    print("Fetching item mapping...")
    item_mapping = get_item_mapping()
    
    if item_mapping is None:
        print("Failed to fetch item mapping")
        return ""
    
    # Determine if input is ID or name
    try:
        item_id = int(item_name_or_id)
        item_info = get_item_by_id(item_mapping, item_id)
        if item_info is None:
            print(f"Item with ID {item_id} not found")
            return ""
        item_name = item_info.get('name', f'Item {item_id}')
    except ValueError:
        # Search by name
        matches = search_item_by_name(item_mapping, item_name_or_id)
        if not matches:
            print(f"No items found matching '{item_name_or_id}'")
            return ""
        if len(matches) > 1:
            print(f"Found {len(matches)} matches for '{item_name_or_id}':")
            for match in matches[:10]:
                print(f"  - ID {match['id']}: {match['name']}")
            if len(matches) > 10:
                print(f"  ... and {len(matches) - 10} more")
            return ""
        
        item_info = matches[0]
        item_id = item_info['id']
        item_name = item_info['name']
    
    print(f"Fetching timeseries for '{item_name}' (ID: {item_id}) with timestep '{timestep}'...")
    timeseries_data = get_item_timeseries(item_id, timestep)
    
    if timeseries_data is None:
        print(f"Failed to fetch timeseries data")
        return ""
    
    # Add metadata to timeseries data
    enriched_data = {
        'item_id': item_id,
        'item_name': item_name,
        'timestamp': datetime.now().isoformat(),
        'data': timeseries_data.get('data', [])
    }
    
    data_points = enriched_data['data']
    print(f"Found {len(data_points)} data points")
    
    if not data_points:
        print("No data points to graph")
        return ""
    
    # Create output path
    os.makedirs(output_dir, exist_ok=True)
    safe_name = item_name.replace(' ', '_').replace("'", '').replace('(', '').replace(')', '').lower()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'{output_dir}/{safe_name}_{item_id}_trend_{timestamp}.png'
    
    # Create graph
    return create_price_trend_graph(enriched_data, output_path)

def generate_comparison_graph(item_names_or_ids: List[str], timestep: str = "5m",
                              output_dir: str = 'data/item_trend_graphs') -> str:
    """
    Generate a comparison graph for multiple items.
    """
    # First get item mapping
    print("Fetching item mapping...")
    item_mapping = get_item_mapping()
    
    if item_mapping is None:
        print("Failed to fetch item mapping")
        return ""
    
    # Collect data for all items
    all_data = []
    for item_query in item_names_or_ids:
        # Determine if input is ID or name
        try:
            item_id = int(item_query)
            item_info = get_item_by_id(item_mapping, item_id)
            if item_info is None:
                print(f"Item with ID {item_id} not found, skipping...")
                continue
            item_name = item_info.get('name', f'Item {item_id}')
        except ValueError:
            # Search by name
            matches = search_item_by_name(item_mapping, item_query)
            if not matches:
                print(f"No items found matching '{item_query}', skipping...")
                continue
            if len(matches) > 1:
                print(f"Multiple matches for '{item_query}', using first: {matches[0]['name']}")
            
            item_info = matches[0]
            item_id = item_info['id']
            item_name = item_info['name']
        
        print(f"Fetching timeseries for '{item_name}' (ID: {item_id})...")
        timeseries_data = get_item_timeseries(item_id, timestep)
        
        if timeseries_data is None:
            print(f"Failed to fetch timeseries for {item_name}, skipping...")
            continue
        
        all_data.append({
            'item_id': item_id,
            'item_name': item_name,
            'data': timeseries_data.get('data', [])
        })
    
    if not all_data:
        print("No data available for any items")
        return ""
    
    # Create comparison figure
    fig = go.Figure()
    
    colors = ['#2ecc71', '#e74c3c', '#3498db', '#9b59b6', '#f1c40f', '#e67e22', '#1abc9c', '#34495e']
    
    for i, item_data in enumerate(all_data):
        item_name = item_data['item_name']
        data_points = item_data['data']
        
        timestamps = []
        avg_prices = []
        
        for point in data_points:
            ts = point.get('timestamp')
            if ts:
                timestamps.append(datetime.fromtimestamp(ts))
                # Use average of high and low prices
                high = point.get('avgHighPrice')
                low = point.get('avgLowPrice')
                if high and low:
                    avg_prices.append((high + low) / 2)
                elif high:
                    avg_prices.append(high)
                elif low:
                    avg_prices.append(low)
                else:
                    avg_prices.append(None)
        
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=avg_prices,
            name=item_name,
            line=dict(color=color, width=2),
            mode='lines',
            hovertemplate='%{y:,.0f} gp<extra>' + item_name + '</extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='Item Price Comparison',
            x=0.5,
            font=dict(size=20)
        ),
        xaxis_title="Date/Time",
        yaxis_title="Price (gp)",
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        margin=dict(l=60, r=40, t=100, b=60)
    )
    
    fig.update_yaxes(tickformat=",")
    
    # Save outputs
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    item_names_str = '_'.join([d['item_name'].replace(' ', '_')[:10] for d in all_data[:3]])
    output_path = f'{output_dir}/comparison_{item_names_str}_{timestamp}.png'
    
    html_path = output_path.replace('.png', '.html')
    fig.write_html(html_path, include_plotlyjs='cdn')
    print(f"Interactive comparison graph saved to {html_path}")
    
    try:
        fig.write_image(output_path, width=1200, height=600, scale=2)
        print(f"Static comparison image saved to {output_path}")
    except Exception as e:
        print(f"Note: Could not save PNG image (kaleido may not be properly installed): {e}")
        print(f"The interactive HTML graph is still available at {html_path}")
    
    return html_path

def list_available_graphs(graphs_dir: str = 'data/item_trend_graphs') -> List[str]:
    """List all available trend graphs"""
    if not os.path.exists(graphs_dir):
        print(f"Graphs directory does not exist: {graphs_dir}")
        return []
    
    graphs = []
    for file in os.listdir(graphs_dir):
        if file.endswith('.png') or file.endswith('.html'):
            graphs.append(file)
    
    graphs.sort(key=lambda x: os.path.getmtime(os.path.join(graphs_dir, x)), reverse=True)
    
    print(f"Available graphs in {graphs_dir}:")
    for i, graph in enumerate(graphs[:20], 1):
        print(f"  {i}. {graph}")
    
    if len(graphs) > 20:
        print(f"  ... and {len(graphs) - 20} more")
    
    return graphs

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python item_trends_graphs.py generate <item_name_or_id> [timestep]")
        print("  python item_trends_graphs.py from_file <json_path>")
        print("  python item_trends_graphs.py compare <item1> <item2> [item3...] [timestep]")
        print("  python item_trends_graphs.py list")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'generate':
        if len(sys.argv) < 3:
            print("Usage: python item_trends_graphs.py generate <item_name_or_id> [timestep]")
            sys.exit(1)
        item_name_or_id = sys.argv[2]
        timestep = sys.argv[3] if len(sys.argv) > 3 else "5m"
        generate_graph_for_item(item_name_or_id, timestep)
    
    elif command == 'from_file':
        if len(sys.argv) < 3:
            print("Usage: python item_trends_graphs.py from_file <json_path>")
            sys.exit(1)
        json_path = sys.argv[2]
        generate_graph_from_file(json_path)
    
    elif command == 'compare':
        if len(sys.argv) < 4:
            print("Usage: python item_trends_graphs.py compare <item1> <item2> [item3...] [timestep]")
            sys.exit(1)
        # Check if last argument is a timestep (5m, 1h, 6h, 24h)
        if sys.argv[-1] in ["5m", "1h", "6h", "24h"]:
            timestep = sys.argv[-1]
            items = sys.argv[2:-1]
        else:
            timestep = "5m"
            items = sys.argv[2:]
        generate_comparison_graph(items, timestep)
    
    elif command == 'list':
        list_available_graphs()
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: generate, from_file, compare, list")
        sys.exit(1)
