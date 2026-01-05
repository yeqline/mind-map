"""
Position persistence for node locations.

This module handles saving and loading node positions to/from
sidecar JSON files, allowing users to manually adjust positions
in Excalidraw and have them preserved across regenerations.
"""

import json
from pathlib import Path
from typing import Optional

from graph import Graph


def get_positions_path(md_path: str) -> Path:
    """
    Get the positions file path for a markdown file.
    
    For notes.md, returns notes.positions.json
    """
    path = Path(md_path)
    return path.with_suffix('.positions.json')


def load_positions(md_path: str) -> dict[str, dict[str, float]]:
    """
    Load saved positions for a markdown file.
    
    Args:
        md_path: Path to the markdown file.
        
    Returns:
        Dictionary mapping node IDs to {x, y} positions.
    """
    positions_path = get_positions_path(md_path)
    
    if not positions_path.exists():
        return {}
    
    try:
        with open(positions_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate structure
        positions = {}
        for node_id, pos in data.items():
            if isinstance(pos, dict) and 'x' in pos and 'y' in pos:
                positions[node_id] = {
                    'x': float(pos['x']),
                    'y': float(pos['y']),
                }
                # Include width/height if present
                if 'width' in pos:
                    positions[node_id]['width'] = float(pos['width'])
                if 'height' in pos:
                    positions[node_id]['height'] = float(pos['height'])
        
        return positions
    except (json.JSONDecodeError, ValueError, TypeError):
        return {}


def save_positions(md_path: str, graph: Graph) -> None:
    """
    Save current node positions to the positions file.
    
    Args:
        md_path: Path to the markdown file.
        graph: Graph with positioned nodes.
    """
    positions_path = get_positions_path(md_path)
    
    positions = {}
    for node in graph.nodes.values():
        positions[node.id] = {
            'x': node.x,
            'y': node.y,
            'width': node.width,
            'height': node.height,
        }
    
    with open(positions_path, 'w', encoding='utf-8') as f:
        json.dump(positions, f, indent=2)


def apply_saved_positions(graph: Graph, positions: dict[str, dict[str, float]]) -> list[str]:
    """
    Apply saved positions to nodes in the graph.
    
    Args:
        graph: Graph with nodes to position.
        positions: Saved positions from load_positions.
        
    Returns:
        List of node IDs that are new (not in saved positions).
    """
    new_nodes = []
    
    for node in graph.nodes.values():
        if node.id in positions:
            pos = positions[node.id]
            node.x = pos['x']
            node.y = pos['y']
            if 'width' in pos:
                node.width = pos['width']
            if 'height' in pos:
                node.height = pos['height']
        else:
            new_nodes.append(node.id)
    
    return new_nodes


def sync_positions_from_excalidraw(excalidraw_path: str, md_path: str) -> int:
    """
    Extract node positions from an Excalidraw file and save them.
    
    This allows users to manually reposition nodes in Excalidraw
    and then sync those positions back to the positions file.
    
    Args:
        excalidraw_path: Path to the .excalidraw file.
        md_path: Path to the source markdown file.
        
    Returns:
        Number of positions synced.
    """
    excalidraw_file = Path(excalidraw_path)
    
    if not excalidraw_file.exists():
        raise FileNotFoundError(f"Excalidraw file not found: {excalidraw_path}")
    
    with open(excalidraw_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    positions = {}
    elements = data.get('elements', [])
    
    for element in elements:
        element_id = element.get('id', '')
        element_type = element.get('type', '')
        
        # Only extract positions from rectangles (node containers)
        # Skip text, arrows, and other elements
        if element_type == 'rectangle' and element_id.startswith('c-'):
            positions[element_id] = {
                'x': element.get('x', 0),
                'y': element.get('y', 0),
                'width': element.get('width', 250),
                'height': element.get('height', 80),
            }
    
    # Save to positions file
    positions_path = get_positions_path(md_path)
    with open(positions_path, 'w', encoding='utf-8') as f:
        json.dump(positions, f, indent=2)
    
    return len(positions)

