"""
Excalidraw JSON generator.

This module generates Excalidraw-compatible JSON files from
Graph structures, applying visual styles from the configuration.

Based on Excalidraw API documentation:
https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api

Element types supported:
- rectangle: For node containers
- text: For node content (bound to rectangles)
- arrow: For directed edges (parent_child, prereqs)
- line: For undirected edges (related, contrasts)
"""

import json
import random
import re
from pathlib import Path
from typing import Any

from graph import Graph, Node, Edge, EdgeType
from config import Config


def _convert_inline_links(text: str) -> str:
    """
    Convert markdown anchor links [Display Text](#c-id) to just the display text.
    
    [SQL Joins](#c-sql-joins) -> "SQL Joins"
    """
    def replace_link(match):
        # Return just the display text
        return match.group(1)
    
    # Match [Display Text](#c-id) pattern
    return re.sub(r'\[([^\]]+)\]\(#c-[\w-]+\)', replace_link, text)


def _wrap_text_for_width(text: str, width: float, font_size: int) -> str:
    """
    Wrap text to fit within a given pixel width.
    
    Excalidraw stores wrapped text in the 'text' field with explicit newlines,
    while 'originalText' keeps the unwrapped version.
    
    Args:
        text: The text to wrap.
        width: Available width in pixels.
        font_size: Font size in pixels.
        
    Returns:
        Text with newlines inserted for word wrapping.
    """
    # Estimate chars per line based on font size
    # For Excalidraw's fonts, average char width is about 0.5 * font_size
    char_width = font_size * 0.5
    max_chars = max(15, int(width / char_width))
    
    lines = text.split('\n')
    wrapped_lines = []
    
    for line in lines:
        if len(line) <= max_chars:
            wrapped_lines.append(line)
            continue
        
        # Wrap this line at word boundaries
        words = line.split(' ')
        current_line = ""
        
        for word in words:
            if not current_line:
                current_line = word
            elif len(current_line) + 1 + len(word) <= max_chars:
                current_line += " " + word
            else:
                wrapped_lines.append(current_line)
                current_line = word
        
        if current_line:
            wrapped_lines.append(current_line)
    
    return '\n'.join(wrapped_lines)



def _estimate_text_dimensions(text: str, font_size: int, max_width: int, padding: int) -> tuple[int, int]:
    """
    Estimate text dimensions for node sizing.
    
    This is an approximation since we don't have actual text rendering.
    Uses rough character-width estimates based on font size.
    
    Args:
        text: The text content.
        font_size: Font size in pixels.
        max_width: Maximum width before wrapping.
        padding: Padding around the text.
        
    Returns:
        Tuple of (width, height) in pixels.
    """
    if not text:
        return (max_width, font_size + padding * 2)
    
    # Estimate average character width (~0.6 * font_size for most fonts)
    char_width = font_size * 0.55
    line_height = font_size * 1.25
    
    # Available width for text (minus padding)
    available_width = max_width - padding * 2
    chars_per_line = max(1, int(available_width / char_width))
    
    lines = text.split('\n')
    total_lines = 0
    
    for line in lines:
        if len(line) == 0:
            total_lines += 1
        else:
            # Estimate wrapped lines
            wrapped_lines = max(1, (len(line) + chars_per_line - 1) // chars_per_line)
            total_lines += wrapped_lines
    
    # Calculate dimensions
    text_height = total_lines * line_height
    height = int(text_height + padding * 2)
    
    # Ensure minimum height
    height = max(height, font_size * 3 + padding * 2)
    
    return (max_width, height)


def _generate_seed() -> int:
    """Generate a random seed for Excalidraw elements."""
    return random.randint(1, 2147483647)


def _create_rectangle(
    node: Node,
    config: Config
) -> dict[str, Any]:
    """
    Create a rectangle element for a node.
    
    Based on Excalidraw ExcalidrawRectangleElement type.
    """
    style = config.get_node_style(node.node_type)
    
    # Check if node has a tag with a custom color
    fill_color = style.fill
    if node.tags:
        tag_color = config.get_tag_color(node.tags[0])
        if tag_color:
            fill_color = tag_color
    
    return {
        "id": node.id,
        "type": "rectangle",
        "x": node.x,
        "y": node.y,
        "width": node.width,
        "height": node.height,
        "angle": 0,
        "strokeColor": style.stroke,
        "backgroundColor": fill_color,
        "fillStyle": "solid",
        "strokeWidth": style.stroke_width,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": {"type": 3},  # Type 3 = rounded corners for rectangles
        "seed": _generate_seed(),
        "version": 1,
        "versionNonce": _generate_seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False
    }


def _create_text(
    node: Node,
    config: Config,
    container_id: str
) -> dict[str, Any]:
    """
    Create a text element for a node's title and content.
    
    Based on Excalidraw ExcalidrawTextElement type.
    Text is bound to a container (rectangle) via containerId.
    """
    style = config.get_node_style(node.node_type)
    
    # Combine title and content
    original_text = node.title
    if node.content.strip():
        # Truncate content if too long for display
        content_preview = node.content.strip()
        if len(content_preview) > 500:
            content_preview = content_preview[:500] + "..."
        # Convert wiki-style links to readable text
        content_preview = _convert_inline_links(content_preview)
        original_text += f"\n\n{content_preview}"
    
    text_id = f"{node.id}-text"
    
    # Text width should be container width minus padding
    text_width = node.width - style.padding * 2
    text_height = node.height - style.padding * 2
    
    # Wrap text for display (Excalidraw stores wrapped in 'text', original in 'originalText')
    wrapped_text = _wrap_text_for_width(original_text, text_width, style.font_size)
    
    return {
        "id": text_id,
        "type": "text",
        "x": node.x + style.padding,
        "y": node.y + style.padding,
        "width": text_width,
        "height": text_height,
        "angle": 0,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": _generate_seed(),
        "version": 2,
        "versionNonce": _generate_seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
        "text": wrapped_text,
        "fontSize": style.font_size,
        "fontFamily": style.font_family,
        "textAlign": "left",
        "verticalAlign": "top",
        "containerId": container_id,
        "originalText": original_text,
        "lineHeight": 1.25,
        "autoResize": True
    }




def _create_edge(
    edge: Edge,
    source_node: Node,
    target_node: Node,
    config: Config
) -> dict[str, Any]:
    """
    Create an arrow element for an edge (with or without arrowheads).
    
    Note: We always use 'arrow' type because 'line' type doesn't support bindings.
    For undirected edges, we just set arrowheads to None.
    """
    style = config.get_edge_style(edge.edge_type)
    
    # For parent-child edges (left-to-right layout): right side of parent to left side of child
    if edge.edge_type == EdgeType.PARENT_CHILD:
        source_x = source_node.x + source_node.width
        source_y = source_node.y + source_node.height / 2
        target_x = target_node.x
        target_y = target_node.y + target_node.height / 2
    else:
        # For other edges: find the best connection points based on relative positions
        source_cx = source_node.x + source_node.width / 2
        source_cy = source_node.y + source_node.height / 2
        target_cx = target_node.x + target_node.width / 2
        target_cy = target_node.y + target_node.height / 2
        
        dx = target_cx - source_cx
        dy = target_cy - source_cy
        
        # Connect from the side that faces the target
        if abs(dx) > abs(dy):
            # Horizontal connection
            if dx > 0:
                source_x = source_node.x + source_node.width
                target_x = target_node.x
            else:
                source_x = source_node.x
                target_x = target_node.x + target_node.width
            source_y = source_cy
            target_y = target_cy
        else:
            # Vertical connection
            if dy > 0:
                source_y = source_node.y + source_node.height
                target_y = target_node.y
            else:
                source_y = source_node.y
                target_y = target_node.y + target_node.height
            source_x = source_cx
            target_x = target_cx
    
    dx = target_x - source_x
    dy = target_y - source_y
    
    return {
        "id": edge.id,
        "type": "arrow",
        "x": source_x,
        "y": source_y,
        "width": abs(dx),
        "height": abs(dy),
        "angle": 0,
        "strokeColor": style.stroke,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": style.stroke_width,
        "strokeStyle": style.stroke_style,
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": _generate_seed(),
        "version": 1,
        "versionNonce": _generate_seed(),
        "isDeleted": False,
        "boundElements": None,
        "updated": 1,
        "link": None,
        "locked": False,
        "points": [
            [0, 0],
            [dx, dy]
        ],
        "lastCommittedPoint": None,
        "startBinding": {
            "elementId": edge.source_id,
            "focus": 0,
            "gap": 8
        },
        "endBinding": {
            "elementId": edge.target_id,
            "focus": 0,
            "gap": 8
        },
        "startArrowhead": style.start_arrowhead,
        "endArrowhead": style.end_arrowhead
    }


def estimate_node_dimensions(graph: Graph, config: Config) -> None:
    """
    Estimate and set node dimensions based on content.
    
    This updates node.width and node.height in the graph based on
    the text content that will be displayed.
    
    Only updates dimensions for nodes that still have default dimensions
    (i.e., haven't been manually resized by the user).
    
    Args:
        graph: Graph with nodes to update.
        config: Configuration with style settings.
    """
    default_width = config.layout.node_width
    default_height = config.layout.node_min_height
    
    for node in graph.nodes.values():
        # Skip if node has been manually resized (not default dimensions)
        # We detect this by checking if dimensions differ significantly from defaults
        if abs(node.height - default_height) > 10:
            # Node was likely manually resized, keep its dimensions
            continue
        
        style = config.get_node_style(node.node_type)
        
        # Build the text content that will be displayed
        text_content = node.title
        if node.content.strip():
            content_preview = node.content.strip()
            if len(content_preview) > 500:
                content_preview = content_preview[:500] + "..."
            content_preview = _convert_inline_links(content_preview)
            text_content += f"\n\n{content_preview}"
        
        # Estimate dimensions
        width, height = _estimate_text_dimensions(
            text_content, 
            style.font_size, 
            default_width, 
            style.padding
        )
        
        node.width = width
        node.height = height


def _generate_group_id() -> str:
    """Generate a unique group ID for Excalidraw."""
    import string
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(21))


def _create_link_block(
    edge: Edge,
    source_node: Node,
    target_node: Node,
    config: Config,
    link_index: int,
    group_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Create a link block (rectangle + text) for an inline link.
    
    The link block is positioned below the source node and grouped with it.
    
    Args:
        edge: The edge representing the inline link.
        source_node: The source node.
        target_node: The target node (for the label).
        config: Configuration for styling.
        link_index: Index of this link (for positioning multiple links).
        group_id: Group ID to associate with the source node.
        
    Returns:
        Tuple of (rectangle_element, text_element).
    """
    # Link block styling
    link_block_height = 50
    link_block_width = 180
    link_gap = 10  # Gap between link blocks
    link_font_size = 16
    link_padding = 8
    
    # Position below the source node
    block_x = source_node.x + link_index * (link_block_width + link_gap)
    block_y = source_node.y + source_node.height + 15
    
    # Create a unique ID for the link block
    link_block_id = f"link-{edge.source_id}-{edge.target_id}"
    link_text_id = f"{link_block_id}-text"
    
    # Get target node title for the label
    label = target_node.title
    
    # Wrap the label text
    wrapped_label = _wrap_text_for_width(label, link_block_width - link_padding * 2, link_font_size)
    
    # Create rectangle
    rect = {
        "id": link_block_id,
        "type": "rectangle",
        "x": block_x,
        "y": block_y,
        "width": link_block_width,
        "height": link_block_height,
        "angle": 0,
        "strokeColor": "#1971c2",  # Blue color for links
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [group_id],
        "frameId": None,
        "roundness": {"type": 3},
        "seed": _generate_seed(),
        "version": 1,
        "versionNonce": _generate_seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False
    }
    
    # Create text
    text = {
        "id": link_text_id,
        "type": "text",
        "x": block_x + link_padding,
        "y": block_y + link_padding,
        "width": link_block_width - link_padding * 2,
        "height": link_block_height - link_padding * 2,
        "angle": 0,
        "strokeColor": "#1971c2",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [group_id],
        "frameId": None,
        "roundness": None,
        "seed": _generate_seed(),
        "version": 2,
        "versionNonce": _generate_seed(),
        "isDeleted": False,
        "boundElements": None,
        "updated": 1,
        "link": None,
        "locked": False,
        "text": wrapped_label,
        "fontSize": link_font_size,
        "fontFamily": 5,  # Font family 5 for links
        "textAlign": "center",
        "verticalAlign": "middle",
        "containerId": link_block_id,
        "originalText": label,
        "autoResize": True,
        "lineHeight": 1.25
    }
    
    # Add text binding to rectangle
    rect["boundElements"].append({
        "type": "text",
        "id": link_text_id
    })
    
    return rect, text


def _create_inline_link_edge(
    edge: Edge,
    link_block_id: str,
    link_block_x: float,
    link_block_y: float,
    link_block_width: float,
    link_block_height: float,
    target_node: Node,
    config: Config
) -> dict[str, Any]:
    """
    Create an arrow from a link block to the target node.
    """
    style = config.get_edge_style(edge.edge_type)
    
    # Start from the link block
    source_cx = link_block_x + link_block_width / 2
    source_cy = link_block_y + link_block_height / 2
    target_cx = target_node.x + target_node.width / 2
    target_cy = target_node.y + target_node.height / 2
    
    dx = target_cx - source_cx
    dy = target_cy - source_cy
    
    # Connect from the side facing the target
    if abs(dx) > abs(dy):
        if dx > 0:
            source_x = link_block_x + link_block_width
            target_x = target_node.x
        else:
            source_x = link_block_x
            target_x = target_node.x + target_node.width
        source_y = source_cy
        target_y = target_cy
    else:
        if dy > 0:
            source_y = link_block_y + link_block_height
            target_y = target_node.y
        else:
            source_y = link_block_y
            target_y = target_node.y + target_node.height
        source_x = source_cx
        target_x = target_cx
    
    arrow_dx = target_x - source_x
    arrow_dy = target_y - source_y
    
    return {
        "id": edge.id,
        "type": "arrow",
        "x": source_x,
        "y": source_y,
        "width": abs(arrow_dx),
        "height": abs(arrow_dy),
        "angle": 0,
        "strokeColor": style.stroke,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": style.stroke_width,
        "strokeStyle": style.stroke_style,
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": _generate_seed(),
        "version": 1,
        "versionNonce": _generate_seed(),
        "isDeleted": False,
        "boundElements": None,
        "updated": 1,
        "link": None,
        "locked": False,
        "points": [
            [0, 0],
            [arrow_dx, arrow_dy]
        ],
        "lastCommittedPoint": None,
        "startBinding": {
            "elementId": link_block_id,
            "focus": 0,
            "gap": 8
        },
        "endBinding": {
            "elementId": edge.target_id,
            "focus": 0,
            "gap": 8
        },
        "startArrowhead": None,
        "endArrowhead": None
    }


def generate_excalidraw(graph: Graph, config: Config) -> dict[str, Any]:
    """
    Generate Excalidraw JSON from a Graph.
    
    Args:
        graph: Graph with positioned nodes and edges.
        config: Configuration for styling.
        
    Returns:
        Dictionary representing the Excalidraw file structure.
    """
    elements = []
    
    # Track bound elements for each node
    bound_elements: dict[str, list[dict]] = {node_id: [] for node_id in graph.nodes}
    
    # Separate inline link edges from other edges
    inline_edges: list[Edge] = []
    regular_edges: list[Edge] = []
    
    for edge in graph.edges:
        if edge.is_inline_link:
            inline_edges.append(edge)
        else:
            regular_edges.append(edge)
    
    # Create regular edges first (non-inline links)
    for edge in regular_edges:
        source_node = graph.get_node(edge.source_id)
        target_node = graph.get_node(edge.target_id)
        
        if not source_node or not target_node:
            continue
        
        element = _create_edge(edge, source_node, target_node, config)
        elements.append(element)
        
        # Track bindings
        if edge.source_id in bound_elements:
            bound_elements[edge.source_id].append({
                "id": edge.id,
                "type": "arrow"
            })
        if edge.target_id in bound_elements:
            bound_elements[edge.target_id].append({
                "id": edge.id,
                "type": "arrow"
            })
    
    # Group inline links by source node
    inline_links_by_source: dict[str, list[Edge]] = {}
    for edge in inline_edges:
        if edge.source_id not in inline_links_by_source:
            inline_links_by_source[edge.source_id] = []
        inline_links_by_source[edge.source_id].append(edge)
    
    # Track link block elements for each node (to add to node's group)
    node_group_ids: dict[str, str] = {}  # node_id -> group_id
    
    # Create link blocks for inline links
    for source_id, edges in inline_links_by_source.items():
        source_node = graph.get_node(source_id)
        if not source_node:
            continue
        
        # Generate a group ID for this node and its link blocks
        group_id = _generate_group_id()
        node_group_ids[source_id] = group_id
        
        # Link block dimensions
        link_block_height = 50
        link_block_width = 180
        link_gap = 10
        
        for i, edge in enumerate(edges):
            target_node = graph.get_node(edge.target_id)
            if not target_node:
                continue
            
            # Create link block
            link_rect, link_text = _create_link_block(
                edge, source_node, target_node, config, i, group_id
            )
            
            # Calculate link block position for the arrow
            block_x = source_node.x + i * (link_block_width + link_gap)
            block_y = source_node.y + source_node.height + 15
            link_block_id = f"link-{edge.source_id}-{edge.target_id}"
            
            # Create arrow from link block to target
            arrow = _create_inline_link_edge(
                edge, link_block_id, block_x, block_y,
                link_block_width, link_block_height, target_node, config
            )
            
            # Add arrow binding to link block
            link_rect["boundElements"].append({
                "id": edge.id,
                "type": "arrow"
            })
            
            # Track binding on target node
            if edge.target_id in bound_elements:
                bound_elements[edge.target_id].append({
                    "id": edge.id,
                    "type": "arrow"
                })
            
            elements.append(link_rect)
            elements.append(link_text)
            elements.append(arrow)
    
    # Create nodes (rectangles + text)
    for node in graph.nodes.values():
        rect = _create_rectangle(node, config)
        text = _create_text(node, config, node.id)
        
        # Add group ID if this node has inline links
        if node.id in node_group_ids:
            rect["groupIds"] = [node_group_ids[node.id]]
            text["groupIds"] = [node_group_ids[node.id]]
        
        # Add bound elements to rectangle
        rect["boundElements"] = bound_elements.get(node.id, [])
        rect["boundElements"].append({
            "id": text["id"],
            "type": "text"
        })
        
        elements.append(rect)
        elements.append(text)
    
    # Build the complete Excalidraw file structure
    excalidraw_data = {
        "type": "excalidraw",
        "version": 2,
        "source": "mind-map-generator",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff"
        },
        "files": {}
    }
    
    return excalidraw_data


def save_excalidraw(graph: Graph, config: Config, output_path: str) -> None:
    """
    Generate and save an Excalidraw file.
    
    Args:
        graph: Graph with positioned nodes and edges.
        config: Configuration for styling.
        output_path: Path to save the .excalidraw file.
    """
    data = generate_excalidraw(graph, config)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def get_excalidraw_path(md_path: str) -> Path:
    """
    Get the default Excalidraw output path for a markdown file.
    
    For notes.md, returns notes.excalidraw
    """
    path = Path(md_path)
    return path.with_suffix('.excalidraw')

