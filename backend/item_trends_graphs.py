# backend/item_trends_graphs.py
import plotly.graph_objects as go
import plotly.io as pio
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

def load_item_history_from_json(item_id: int, directory: str = "backend/item_prices_json") -> Optional[Dict[str, Any]]:
    """Load item price history from JSON file"""
    file_path = os.path.join(directory, f"item_{item_id}_history.json")
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    else:
        print(f"Error: JSON file {file_path} not found")
        return None

def generate_item_trend_graph(item_id: int, item_name: str, history_data: Dict[str, Any], directory: str = "backend/item_trends_graphs"):
    """Generate item price trend graph using Plotly"""
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Extract data from history
    data = history_data['data'][str(item_id)]
    timestamps = data['timestamps']
    avg_high_prices = data['avgHighPrice']
    avg_low_prices = data['avgLowPrice']
    high_volume = data['highPriceVolume']
    low_volume = data['lowPriceVolume']
    
    # Convert timestamps to datetime objects
    dates = [datetime.fromtimestamp(ts) for ts in timestamps]
    
    # Create figure
    fig = go.Figure()
    
    # Add average high price trace
    fig.add_trace(go.Scatter(
        x=dates,
        y=avg_high_prices,
        name='Average High Price',
        line=dict(color='green', width=2),
        yaxis='y1'
    ))
    
    # Add average low price trace
    fig.add_trace(go.Scatter(
        x=dates,
        y=avg_low_prices,
        name='Average Low Price',
        line=dict(color='red', width=2),
        yaxis='y1'
    ))
    
    # Add high volume trace
    fig.add_trace(go.Bar(
        x=dates,
        y=high_volume,
        name='High Volume',
        marker=dict(color='rgba(0, 255, 0, 0.3)'),
        yaxis='y2'
    ))
    
    # Add low volume trace
    fig.add_trace(go.Bar(
        x=dates,
        y=low_volume,
        name='Low Volume',
        marker=dict(color='rgba(255, 0, 0, 0.3)'),
        yaxis='y2'
    ))
    
    # Update layout
    fig.update_layout(
        title=f'OSRS Item Price Trend: {item_name} (ID: {item_id})',
        xaxis_title='Date',
        yaxis_title='Price (GP)',
        yaxis=dict(title='Price (GP)', side='left'),
        yaxis2=dict(title='Volume', side='right', overlaying='y', showgrid=False),
        legend=dict(x=0, y=1, traceorder='normal'),
        hovermode='x unified',
        template='plotly_dark',
        height=600,
        width=1200
    )
    
    # Save figure as PNG
    file_path = os.path.join(directory, f"item_{item_id}_trend_graph.png")
    pio.write_image(fig, file_path, format='png', scale=2)
    
    print(f"Graph saved to {file_path}")
    
    return file_path

def generate_multiple_item_trend_graphs(item_ids: list, directory: str = "backend/item_trends_graphs"):
    """Generate trend graphs for multiple items"""
    # Import get_item_name from item_prices.py
    from item_prices import get_item_name
    
    for item_id in item_ids:
        # Load history data
        history_data = load_item_history_from_json(item_id)
        if not history_data:
            continue
        
        # Get item name
        item_name = get_item_name(item_id)
        if not item_name:
            item_name = f"Item {item_id}"
        
        # Generate graph
        generate_item_trend_graph(item_id, item_name, history_data, directory)

def generate_item_comparison_graph(item_ids: list, item_names: list, directory: str = "backend/item_trends_graphs"):
    """Generate comparison graph for multiple items"""
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    fig = go.Figure()
    
    for i, item_id in enumerate(item_ids):
        # Load history data
        history_data = load_item_history_from_json(item_id)
        if not history_data:
            continue
        
        # Extract data from history
        data = history_data['data'][str(item_id)]
        timestamps = data['timestamps']
        avg_high_prices = data['avgHighPrice']
        
        # Convert timestamps to datetime objects
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Add trace for each item
        fig.add_trace(go.Scatter(
            x=dates,
            y=avg_high_prices,
            name=item_names[i],
            line=dict(width=2)
        ))
    
    # Update layout
    fig.update_layout(
        title='OSRS Item Price Comparison',
        xaxis_title='Date',
        yaxis_title='Price (GP)',
        legend=dict(x=0, y=1, traceorder='normal'),
        hovermode='x unified',
        template='plotly_dark',
        height=600,
        width=1200
    )
    
    # Save figure as PNG
    file_path = os.path.join(directory, "item_comparison_graph.png")
    pio.write_image(fig, file_path, format='png', scale=2)
    
    print(f"Comparison graph saved to {file_path}")
    
    return file_path

if __name__ == "__main__":
    # Example usage
    item_ids = [4151, 13190, 11730]  # Abyssal whip, Dragon hunter crossbow, Twisted bow
    
    # Generate trend graphs for each item
    generate_multiple_item_trend_graphs(item_ids)
    
    # Generate comparison graph
    item_names = ["Abyssal Whip", "Dragon Hunter Crossbow", "Twisted Bow"]
    generate_item_comparison_graph(item_ids, item_names)