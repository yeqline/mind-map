"""
Auto-layout algorithms for positioning nodes.

This module provides layout algorithms to automatically position
nodes in a visually pleasing arrangement.
"""

from graph import Graph, Node
from config import Config


def apply_layout(graph: Graph, config: Config, nodes_to_position: list[str] | None = None) -> None:
    """
    Apply auto-layout to position nodes in the graph.
    
    Args:
        graph: Graph with nodes to position.
        config: Configuration with layout settings.
        nodes_to_position: Optional list of node IDs to position. If None, positions all nodes.
                          If empty list, positions no nodes (all have saved positions).
    """
    # If no new nodes need positioning, skip layout
    if nodes_to_position is not None and len(nodes_to_position) == 0:
        return
    
    layout_type = config.layout.auto_layout
    
    if layout_type == "tree":
        _apply_tree_layout(graph, config, nodes_to_position)
    elif layout_type == "force":
        _apply_force_layout(graph, config, nodes_to_position)
    # "none" means don't apply any layout


def _apply_tree_layout(graph: Graph, config: Config, nodes_to_position: list[str] | None = None) -> None:
    """
    Apply tree layout algorithm (left-to-right).
    
    Arranges nodes in a hierarchical tree structure based on
    parent-child relationships inferred from heading hierarchy.
    Parents are on the left, children extend to the right.
    
    Args:
        graph: Graph with nodes to position.
        config: Configuration with layout settings.
        nodes_to_position: Optional list of node IDs to position. If None, positions all nodes.
    """
    node_width = config.layout.node_width
    node_height = config.layout.node_min_height
    h_gap = config.layout.horizontal_gap
    v_gap = config.layout.vertical_gap
    
    # Convert to set for fast lookup
    nodes_to_pos_set = set(nodes_to_position) if nodes_to_position is not None else None
    
    # Get root nodes (no parent)
    roots = graph.get_root_nodes()
    
    if not roots:
        return
    
    # Calculate subtree heights for proper spacing (vertical extent)
    subtree_heights: dict[str, float] = {}
    _calculate_subtree_heights(graph, subtree_heights, node_height, v_gap)
    
    # Position each root tree (stacked vertically)
    current_y = 0
    for root in sorted(roots, key=lambda n: n.id):
        _position_subtree_horizontal(
            graph, root, 0, current_y, 
            subtree_heights, node_width, node_height, h_gap, v_gap,
            nodes_to_pos_set
        )
        current_y += subtree_heights.get(root.id, node_height) + v_gap * 2


def _calculate_subtree_heights(
    graph: Graph, 
    heights: dict[str, float],
    default_node_height: float,
    v_gap: float
) -> float:
    """Calculate height needed for each subtree (for left-to-right layout).
    
    Uses actual node heights (from estimate_node_dimensions) for proper spacing.
    """
    for node in graph.nodes.values():
        # Use actual node height if available, otherwise use default
        actual_height = node.height if node.height > 0 else default_node_height
        children = graph.get_children(node.id)
        if not children:
            heights[node.id] = actual_height
        else:
            # Calculate children heights first
            total_children_height = 0
            for child in children:
                if child.id not in heights:
                    _calculate_subtree_height_recursive(
                        graph, child.id, heights, default_node_height, v_gap
                    )
                total_children_height += heights.get(child.id, default_node_height)
            
            # Add gaps between children
            total_children_height += v_gap * (len(children) - 1) if len(children) > 1 else 0
            
            # Subtree height is max of node's own height and total children height
            heights[node.id] = max(actual_height, total_children_height)
    
    return sum(heights.get(r.id, default_node_height) for r in graph.get_root_nodes())


def _calculate_subtree_height_recursive(
    graph: Graph,
    node_id: str,
    heights: dict[str, float],
    default_node_height: float,
    v_gap: float
) -> None:
    """Recursively calculate subtree height for a node."""
    node = graph.get_node(node_id)
    actual_height = node.height if node and node.height > 0 else default_node_height
    
    children = graph.get_children(node_id)
    
    if not children:
        heights[node_id] = actual_height
        return
    
    # Calculate children heights first
    total_children_height = 0
    for child in children:
        if child.id not in heights:
            _calculate_subtree_height_recursive(graph, child.id, heights, default_node_height, v_gap)
        total_children_height += heights.get(child.id, default_node_height)
    
    # Add gaps between children
    if len(children) > 1:
        total_children_height += v_gap * (len(children) - 1)
    
    heights[node_id] = max(actual_height, total_children_height)


def _position_subtree_horizontal(
    graph: Graph,
    node: Node,
    x: float,
    y: float,
    subtree_heights: dict[str, float],
    default_node_width: float,
    default_node_height: float,
    h_gap: float,
    v_gap: float,
    nodes_to_position: set[str] | None = None
) -> None:
    """Position a node and its children recursively (left-to-right layout).
    
    Args:
        nodes_to_position: If provided, only position nodes in this set.
                          If None, position all nodes.
    """
    subtree_height = subtree_heights.get(node.id, default_node_height)
    actual_node_height = node.height if node.height > 0 else default_node_height
    actual_node_width = node.width if node.width > 0 else default_node_width
    
    # Only update position if this node needs positioning
    if nodes_to_position is None or node.id in nodes_to_position:
        # Center the node vertically in its subtree height
        node.x = x
        node.y = y + (subtree_height - actual_node_height) / 2
        # Note: width and height are set by estimate_node_dimensions, not here
    
    # Position children to the right
    children = sorted(graph.get_children(node.id), key=lambda n: n.id)
    if not children:
        return
    
    # Calculate starting position for children (to the right of this node)
    child_x = x + actual_node_width + h_gap
    child_y = y
    
    for child in children:
        child_height = subtree_heights.get(child.id, default_node_height)
        _position_subtree_horizontal(
            graph, child, child_x, child_y,
            subtree_heights, default_node_width, default_node_height, h_gap, v_gap,
            nodes_to_position
        )
        child_y += child_height + v_gap


def _apply_force_layout(graph: Graph, config: Config, nodes_to_position: list[str] | None = None) -> None:
    """
    Apply force-directed layout algorithm.
    
    Uses a simplified force-directed approach with:
    - Repulsion between all nodes
    - Attraction along edges
    
    Args:
        nodes_to_position: Optional list of node IDs to position. If None, positions all nodes.
    """
    node_width = config.layout.node_width
    node_height = config.layout.node_min_height
    
    # Convert to set for fast lookup
    nodes_to_pos_set = set(nodes_to_position) if nodes_to_position is not None else None
    
    # Get nodes that need positioning
    all_nodes = list(graph.nodes.values())
    if nodes_to_pos_set is not None:
        nodes = [n for n in all_nodes if n.id in nodes_to_pos_set]
    else:
        nodes = all_nodes
    
    if not nodes:
        return
    
    cols = max(1, int(len(nodes) ** 0.5))
    
    for i, node in enumerate(nodes):
        row = i // cols
        col = i % cols
        node.x = col * (node_width + config.layout.horizontal_gap)
        node.y = row * (node_height + config.layout.vertical_gap)
        # Note: width and height are set by estimate_node_dimensions, not here
    
    # Simple force-directed iterations
    iterations = 50
    repulsion = 5000
    attraction = 0.01
    damping = 0.9
    
    velocities: dict[str, tuple[float, float]] = {n.id: (0.0, 0.0) for n in nodes}
    
    for _ in range(iterations):
        forces: dict[str, tuple[float, float]] = {n.id: (0.0, 0.0) for n in nodes}
        
        # Repulsion between all pairs
        for i, n1 in enumerate(nodes):
            for n2 in nodes[i+1:]:
                dx = n1.x - n2.x
                dy = n1.y - n2.y
                dist_sq = dx*dx + dy*dy + 1  # Avoid division by zero
                dist = dist_sq ** 0.5
                
                # Repulsion force
                force = repulsion / dist_sq
                fx = force * dx / dist
                fy = force * dy / dist
                
                forces[n1.id] = (forces[n1.id][0] + fx, forces[n1.id][1] + fy)
                forces[n2.id] = (forces[n2.id][0] - fx, forces[n2.id][1] - fy)
        
        # Attraction along edges
        for edge in graph.edges:
            n1 = graph.get_node(edge.source_id)
            n2 = graph.get_node(edge.target_id)
            if n1 and n2:
                dx = n2.x - n1.x
                dy = n2.y - n1.y
                dist = (dx*dx + dy*dy) ** 0.5 + 1
                
                # Attraction force
                force = attraction * dist
                fx = force * dx / dist
                fy = force * dy / dist
                
                forces[n1.id] = (forces[n1.id][0] + fx, forces[n1.id][1] + fy)
                forces[n2.id] = (forces[n2.id][0] - fx, forces[n2.id][1] - fy)
        
        # Apply forces
        for node in nodes:
            vx, vy = velocities[node.id]
            fx, fy = forces[node.id]
            
            vx = (vx + fx) * damping
            vy = (vy + fy) * damping
            
            velocities[node.id] = (vx, vy)
            node.x += vx
            node.y += vy
    
    # Normalize positions to start from (0, 0)
    if nodes:
        min_x = min(n.x for n in nodes)
        min_y = min(n.y for n in nodes)
        for node in nodes:
            node.x -= min_x
            node.y -= min_y

