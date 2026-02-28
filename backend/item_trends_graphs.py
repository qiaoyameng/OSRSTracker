# backend/item_trends_graphs.py
import json
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ITEM_PRICES_DIR = os.path.join(os.path.dirname(__file__), 'item_prices')
ITEM_GRAPHS_DIR = os.path.join(os.path.dirname(__file__), 'item_graphs')


def ensure_graphs_directory_exists():
    """Create the item graphs directory if it doesn't exist."""
    os.makedirs(ITEM_GRAPHS_DIR, exist_ok=True)


def load_item_price_data(item_id: int) -> Optional[Dict[str, Any]]:
    """Load item price data from JSON file."""
    if not os.path.exists(ITEM_PRICES_DIR):
        return None
    
    for filename in os.listdir(ITEM_PRICES_DIR):
        if filename.startswith(f"{item_id}_") and filename.endswith('.json'):
            filepath = os.path.join(ITEM_PRICES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    return None


def load_all_item_price_data() -> List[Dict[str, Any]]:
    """Load all item price data from JSON files."""
    if not os.path.exists(ITEM_PRICES_DIR):
        return []
    
    items = []
    for filename in os.listdir(ITEM_PRICES_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(ITEM_PRICES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                items.append(json.load(f))
    
    return items


def format_price(price: float) -> str:
    """Format price for display."""
    if price >= 1000000000:
        return f"{price / 1000000000:.2f}B"
    elif price >= 1000000:
        return f"{price / 1000000:.2f}M"
    elif price >= 1000:
        return f"{price / 1000:.2f}K"
    else:
        return f"{price:.2f}"


def create_price_trend_graph(item_data: Dict[str, Any], days: int = 180) -> Optional[go.Figure]:
    """Create a price trend graph for an item using Plotly."""
    price_history = item_data.get('price_history')
    
    if not price_history:
        print(f"No price history available for {item_data.get('item_name', 'Unknown')}")
        return None
    
    daily_data = price_history.get('daily', [])
    average_data = price_history.get('average', [])
    
    if not daily_data:
        print(f"No daily price data available for {item_data.get('item_name', 'Unknown')}")
        return None
    
    daily_data = daily_data[-days:] if len(daily_data) > days else daily_data
    average_data = average_data[-days:] if len(average_data) > days else average_data
    
    dates = [d['date'] for d in daily_data]
    daily_prices = [d['price'] for d in daily_data]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=daily_prices,
        mode='lines',
        name='Daily Price',
        line=dict(color='#00D4AA', width=2),
        hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: %{y:,.0f} gp<extra></extra>'
    ))
    
    if average_data:
        avg_dates = [d['date'] for d in average_data]
        avg_prices = [d['price'] for d in average_data]
        fig.add_trace(go.Scatter(
            x=avg_dates,
            y=avg_prices,
            mode='lines',
            name='30-Day Average',
            line=dict(color='#FFD700', width=2, dash='dash'),
            hovertemplate='<b>Date</b>: %{x}<br><b>Avg Price</b>: %{y:,.0f} gp<extra></extra>'
        ))
    
    item_name = item_data.get('item_name', 'Unknown Item')
    current_price = item_data.get('current_price', {})
    current_price_str = current_price.get('price_str', 'N/A')
    
    fig.update_layout(
        title=dict(
            text=f"{item_name} - Price Trend<br><sub>Current Price: {current_price_str} gp</sub>",
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#FFFFFF')
        ),
        xaxis=dict(
            title='Date',
            gridcolor='#333333',
            tickfont=dict(color='#CCCCCC'),
            title_font=dict(color='#FFFFFF')
        ),
        yaxis=dict(
            title='Price (gp)',
            gridcolor='#333333',
            tickfont=dict(color='#CCCCCC'),
            title_font=dict(color='#FFFFFF'),
            tickformat=',.0f'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color='#FFFFFF')
        ),
        plot_bgcolor='#1a1a2e',
        paper_bgcolor='#1a1a2e',
        font=dict(color='#FFFFFF'),
        hovermode='x unified',
        margin=dict(l=60, r=40, t=80, b=60)
    )
    
    fig.update_xaxes(showline=True, linewidth=1, linecolor='#333333', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='#333333', mirror=True)
    
    return fig


def create_multi_item_comparison_graph(items_data: List[Dict[str, Any]], days: int = 180) -> Optional[go.Figure]:
    """Create a comparison graph for multiple items."""
    if not items_data:
        return None
    
    fig = go.Figure()
    
    colors = [
        '#00D4AA', '#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3',
        '#F38181', '#AA96DA', '#FCBAD3', '#A8D8EA', '#F9ED69'
    ]
    
    for idx, item_data in enumerate(items_data):
        price_history = item_data.get('price_history', {})
        daily_data = price_history.get('daily', [])
        
        if not daily_data:
            continue
        
        daily_data = daily_data[-days:] if len(daily_data) > days else daily_data
        
        dates = [d['date'] for d in daily_data]
        prices = [d['price'] for d in daily_data]
        
        item_name = item_data.get('item_name', f'Item {idx}')
        color = colors[idx % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name=item_name,
            line=dict(color=color, width=2),
            hovertemplate=f'<b>{item_name}</b><br>Date: %{{x}}<br>Price: %{{y:,.0f}} gp<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text="Item Price Comparison",
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#FFFFFF')
        ),
        xaxis=dict(
            title='Date',
            gridcolor='#333333',
            tickfont=dict(color='#CCCCCC'),
            title_font=dict(color='#FFFFFF')
        ),
        yaxis=dict(
            title='Price (gp)',
            gridcolor='#333333',
            tickfont=dict(color='#CCCCCC'),
            title_font=dict(color='#FFFFFF'),
            tickformat=',.0f'
        ),
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='left',
            x=1.02,
            font=dict(color='#FFFFFF')
        ),
        plot_bgcolor='#1a1a2e',
        paper_bgcolor='#1a1a2e',
        font=dict(color='#FFFFFF'),
        hovermode='x unified',
        margin=dict(l=60, r=120, t=80, b=60)
    )
    
    fig.update_xaxes(showline=True, linewidth=1, linecolor='#333333', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='#333333', mirror=True)
    
    return fig


def create_price_change_graph(item_data: Dict[str, Any], days: int = 180) -> Optional[go.Figure]:
    """Create a price change percentage graph for an item."""
    price_history = item_data.get('price_history')
    
    if not price_history:
        return None
    
    daily_data = price_history.get('daily', [])
    
    if not daily_data or len(daily_data) < 2:
        return None
    
    daily_data = daily_data[-days:] if len(daily_data) > days else daily_data
    
    dates = [d['date'] for d in daily_data]
    prices = [d['price'] for d in daily_data]
    
    base_price = prices[0]
    if base_price == 0:
        base_price = 1
    
    price_changes = [(p - base_price) / base_price * 100 for p in prices]
    
    colors = ['#00D4AA' if change >= 0 else '#FF6B6B' for change in price_changes]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates,
        y=price_changes,
        name='Price Change %',
        marker_color=price_changes,
        marker_colorscale=[[0, '#FF6B6B'], [0.5, '#333333'], [1, '#00D4AA']],
        marker_cmid=0,
        hovertemplate='<b>Date</b>: %{x}<br><b>Change</b>: %{y:.2f}%<extra></extra>'
    ))
    
    item_name = item_data.get('item_name', 'Unknown Item')
    
    fig.update_layout(
        title=dict(
            text=f"{item_name} - Price Change from Start",
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#FFFFFF')
        ),
        xaxis=dict(
            title='Date',
            gridcolor='#333333',
            tickfont=dict(color='#CCCCCC'),
            title_font=dict(color='#FFFFFF')
        ),
        yaxis=dict(
            title='Price Change (%)',
            gridcolor='#333333',
            tickfont=dict(color='#CCCCCC'),
            title_font=dict(color='#FFFFFF'),
            ticksuffix='%'
        ),
        plot_bgcolor='#1a1a2e',
        paper_bgcolor='#1a1a2e',
        font=dict(color='#FFFFFF'),
        hovermode='x',
        margin=dict(l=60, r=40, t=80, b=60),
        bargap=0
    )
    
    fig.update_xaxes(showline=True, linewidth=1, linecolor='#333333', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='#333333', mirror=True)
    
    return fig


def save_graph_as_image(fig: go.Figure, item_id: int, item_name: str, graph_type: str = 'trend') -> str:
    """Save a Plotly figure as an image file."""
    ensure_graphs_directory_exists()
    
    safe_name = item_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = f"{item_id}_{safe_name}_{graph_type}.png"
    filepath = os.path.join(ITEM_GRAPHS_DIR, filename)
    
    fig.write_image(filepath, scale=2)
    print(f"Saved graph: {filepath}")
    
    return filepath


def save_graph_as_html(fig: go.Figure, item_id: int, item_name: str, graph_type: str = 'trend') -> str:
    """Save a Plotly figure as an HTML file."""
    ensure_graphs_directory_exists()
    
    safe_name = item_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = f"{item_id}_{safe_name}_{graph_type}.html"
    filepath = os.path.join(ITEM_GRAPHS_DIR, filename)
    
    fig.write_html(filepath, include_plotlyjs=True)
    print(f"Saved HTML graph: {filepath}")
    
    return filepath


def generate_item_trend_graph(item_id: int, days: int = 180, save_html: bool = False) -> Optional[str]:
    """Generate and save a price trend graph for a single item."""
    item_data = load_item_price_data(item_id)
    
    if not item_data:
        print(f"No price data found for item ID: {item_id}")
        return None
    
    fig = create_price_trend_graph(item_data, days)
    
    if not fig:
        return None
    
    item_name = item_data.get('item_name', 'Unknown')
    filepath = save_graph_as_image(fig, item_id, item_name, f'trend_{days}d')
    
    if save_html:
        save_graph_as_html(fig, item_id, item_name, f'trend_{days}d')
    
    return filepath


def generate_item_change_graph(item_id: int, days: int = 180, save_html: bool = False) -> Optional[str]:
    """Generate and save a price change graph for a single item."""
    item_data = load_item_price_data(item_id)
    
    if not item_data:
        print(f"No price data found for item ID: {item_id}")
        return None
    
    fig = create_price_change_graph(item_data, days)
    
    if not fig:
        return None
    
    item_name = item_data.get('item_name', 'Unknown')
    filepath = save_graph_as_image(fig, item_id, item_name, f'change_{days}d')
    
    if save_html:
        save_graph_as_html(fig, item_id, item_name, f'change_{days}d')
    
    return filepath


def generate_all_item_graphs(days: int = 180, save_html: bool = False) -> List[str]:
    """Generate trend graphs for all saved items."""
    items_data = load_all_item_price_data()
    
    if not items_data:
        print("No item price data found. Run item_prices.py first.")
        return []
    
    print(f"Generating graphs for {len(items_data)} items...")
    
    saved_paths = []
    for item_data in items_data:
        item_id = item_data.get('item_id')
        item_name = item_data.get('item_name', 'Unknown')
        
        print(f"\nProcessing: {item_name}")
        
        fig = create_price_trend_graph(item_data, days)
        if fig:
            filepath = save_graph_as_image(fig, item_id, item_name, f'trend_{days}d')
            saved_paths.append(filepath)
            
            if save_html:
                save_graph_as_html(fig, item_id, item_name, f'trend_{days}d')
    
    print(f"\nGenerated {len(saved_paths)} graphs")
    return saved_paths


def generate_comparison_graph(item_ids: List[int], days: int = 180, save_html: bool = False) -> Optional[str]:
    """Generate a comparison graph for multiple items."""
    items_data = []
    
    for item_id in item_ids:
        item_data = load_item_price_data(item_id)
        if item_data:
            items_data.append(item_data)
        else:
            print(f"Warning: No data found for item ID {item_id}")
    
    if not items_data:
        print("No item data found for comparison")
        return None
    
    fig = create_multi_item_comparison_graph(items_data, days)
    
    if not fig:
        return None
    
    ids_str = '_'.join(map(str, item_ids[:5]))
    if len(item_ids) > 5:
        ids_str += f'_plus{len(item_ids) - 5}'
    
    filename = f"comparison_{ids_str}_{days}d.png"
    filepath = os.path.join(ITEM_GRAPHS_DIR, filename)
    
    ensure_graphs_directory_exists()
    fig.write_image(filepath, scale=2)
    print(f"Saved comparison graph: {filepath}")
    
    if save_html:
        html_filepath = filepath.replace('.png', '.html')
        fig.write_html(html_filepath, include_plotlyjs=True)
        print(f"Saved HTML comparison graph: {html_filepath}")
    
    return filepath


def list_generated_graphs() -> List[Dict[str, Any]]:
    """List all generated graph files."""
    if not os.path.exists(ITEM_GRAPHS_DIR):
        return []
    
    graphs = []
    for filename in os.listdir(ITEM_GRAPHS_DIR):
        if filename.endswith(('.png', '.html')):
            filepath = os.path.join(ITEM_GRAPHS_DIR, filename)
            graphs.append({
                'filename': filename,
                'filepath': filepath,
                'size': os.path.getsize(filepath),
                'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
            })
    
    return graphs


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python item_trends_graphs.py generate_item_trend_graph <item_id> [days] [--html]")
        print("  python item_trends_graphs.py generate_item_change_graph <item_id> [days] [--html]")
        print("  python item_trends_graphs.py generate_all_item_graphs [days] [--html]")
        print("  python item_trends_graphs.py generate_comparison_graph <item_id1,item_id2,...> [days] [--html]")
        print("  python item_trends_graphs.py list_generated_graphs")
        sys.exit(1)
    
    command = sys.argv[1]
    save_html = '--html' in sys.argv
    args = [arg for arg in sys.argv[2:] if arg != '--html']
    
    if command == 'generate_item_trend_graph':
        if len(args) < 1:
            print("Error: item_id required")
            sys.exit(1)
        item_id = int(args[0])
        days = int(args[1]) if len(args) > 1 else 180
        generate_item_trend_graph(item_id, days, save_html)
    
    elif command == 'generate_item_change_graph':
        if len(args) < 1:
            print("Error: item_id required")
            sys.exit(1)
        item_id = int(args[0])
        days = int(args[1]) if len(args) > 1 else 180
        generate_item_change_graph(item_id, days, save_html)
    
    elif command == 'generate_all_item_graphs':
        days = int(args[0]) if args else 180
        generate_all_item_graphs(days, save_html)
    
    elif command == 'generate_comparison_graph':
        if len(args) < 1:
            print("Error: comma-separated item_ids required")
            sys.exit(1)
        item_ids = [int(x.strip()) for x in args[0].split(',')]
        days = int(args[1]) if len(args) > 1 else 180
        generate_comparison_graph(item_ids, days, save_html)
    
    elif command == 'list_generated_graphs':
        graphs = list_generated_graphs()
        for graph in graphs:
            print(f"  {graph['filename']} ({graph['size']} bytes)")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
