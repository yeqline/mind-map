"""
Graph data structures for mind-map nodes and edges.

This module defines the core data structures used throughout the application:
- Node: Represents a concept/heading in the markdown file
- Edge: Represents a relationship between nodes
- Graph: Container for all nodes and edges from a markdown file
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class NodeType(Enum):
    """Valid node types (exhaustive list per manifest)."""
    CONCEPT = "concept"
    EXAMPLE = "example"
    CODE = "code"
    TABLE = "table"


class EdgeType(Enum):
    """Valid edge types (exhaustive list per manifest)."""
    PARENT_CHILD = "parent_child"  # Inferred from heading hierarchy
    PREREQS = "prereqs"            # From edges fence
    RELATED = "related"            # From edges fence or inline links
    CONTRASTS = "contrasts"        # From edges fence


@dataclass
class Node:
    """
    Represents a node (concept) in the mind map.
    
    Attributes:
        id: Globally unique identifier (e.g., "c-sql-joins")
        title: Display title from the heading
        level: Heading level (2 for ##, 3 for ###, etc.)
        node_type: One of NodeType enum values
        tags: List of tags from config.yaml
        content: Markdown content below the heading
        parent_id: ID of parent node (inferred from heading hierarchy)
        x: X position (from positions file or auto-layout)
        y: Y position (from positions file or auto-layout)
        width: Calculated width based on content
        height: Calculated height based on content
    """
    id: str
    title: str
    level: int
    node_type: NodeType = NodeType.CONCEPT
    tags: list[str] = field(default_factory=list)
    content: str = ""
    parent_id: Optional[str] = None
    x: float = 0.0
    y: float = 0.0
    width: float = 250.0
    height: float = 80.0


@dataclass
class Edge:
    """
    Represents an edge (relationship) between two nodes.
    
    Attributes:
        source_id: ID of the source node
        target_id: ID of the target node
        edge_type: One of EdgeType enum values
        is_inline_link: True if this edge comes from an inline [[c-id]] link
    """
    source_id: str
    target_id: str
    edge_type: EdgeType
    is_inline_link: bool = False
    
    @property
    def id(self) -> str:
        """Generate unique edge ID."""
        return f"edge-{self.source_id}-{self.target_id}-{self.edge_type.value}"


@dataclass
class Graph:
    """
    Container for all nodes and edges from a markdown file.
    
    Attributes:
        nodes: Dictionary mapping node IDs to Node objects
        edges: List of Edge objects
        source_file: Path to the source markdown file
    """
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    source_file: str = ""
    
    def add_node(self, node: Node) -> None:
        """Add a node to the graph. Raises error on duplicate ID."""
        if node.id in self.nodes:
            raise ValueError(f"Duplicate node ID: {node.id}")
        self.nodes[node.id] = node
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph. Deduplicates by (source, target, type)."""
        # Check for duplicates
        for existing in self.edges:
            if (existing.source_id == edge.source_id and 
                existing.target_id == edge.target_id and 
                existing.edge_type == edge.edge_type):
                return  # Already exists, skip
        self.edges.append(edge)
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID, or None if not found."""
        return self.nodes.get(node_id)
    
    def get_children(self, node_id: str) -> list[Node]:
        """Get all child nodes of a given node."""
        return [n for n in self.nodes.values() if n.parent_id == node_id]
    
    def get_root_nodes(self) -> list[Node]:
        """Get all nodes without parents (top-level nodes)."""
        return [n for n in self.nodes.values() if n.parent_id is None]
    
    def validate(self) -> list[str]:
        """
        Validate the graph and return list of warnings.
        
        Checks:
        - All edge targets exist
        - No duplicate node IDs (enforced by add_node)
        """
        warnings = []
        
        for edge in self.edges:
            if edge.source_id not in self.nodes:
                warnings.append(f"Edge source not found: {edge.source_id}")
            if edge.target_id not in self.nodes:
                warnings.append(f"Edge target not found: {edge.target_id}")
        
        return warnings

