"""
Markdown parser for mind-map files.

Parses markdown files following the manifest.md convention and
extracts nodes, edges, and metadata into a Graph structure.
"""

import re
from pathlib import Path
from typing import Optional

from graph import Graph, Node, Edge, NodeType, EdgeType
from config import Config


# Regex patterns
HEADING_PATTERN = re.compile(r'^(#{2,6})\s+(.+?)\s*\{#(c-[\w-]+)\}\s*$')
META_START_PATTERN = re.compile(r'^>\s*\[!meta\]\s*$')
META_LINE_PATTERN = re.compile(r'^>\s*(\w+):\s*(.*)$')
EDGES_START_PATTERN = re.compile(r'^```edges\s*$')
EDGES_END_PATTERN = re.compile(r'^```\s*$')
EDGE_LINE_PATTERN = re.compile(r'^(\w+):\s*(.+)$')
# Matches markdown links to anchors: [Display Text](#c-some-id)
INLINE_LINK_PATTERN = re.compile(r'\[[^\]]+\]\(#(c-[\w-]+)\)')
IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
URL_PATTERN = re.compile(r'\[([^\]]+)\]\((https?://[^)]+)\)')


class ParseError(Exception):
    """Raised when parsing fails."""
    pass


class ParseWarning:
    """Represents a non-fatal parsing issue."""
    def __init__(self, message: str, line_number: Optional[int] = None):
        self.message = message
        self.line_number = line_number
    
    def __str__(self):
        if self.line_number:
            return f"Line {self.line_number}: {self.message}"
        return self.message


class Parser:
    """
    Parses markdown files into Graph structures.
    
    The parser follows these rules from manifest.md:
    - Nodes: Headings with {#c-...} anchors
    - Meta: [!meta] blockquote with tags/type
    - Edges: ```edges fence with prereqs/related/contrasts
    - Inline links: [text](#c-...) become related edges
    - Parent-child: Inferred from heading hierarchy
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.warnings: list[ParseWarning] = []
    
    def parse_file(self, file_path: str) -> Graph:
        """
        Parse a markdown file into a Graph.
        
        Args:
            file_path: Path to the markdown file.
            
        Returns:
            Graph containing all nodes and edges.
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            ParseError: If parsing fails critically.
        """
        self.warnings = []
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content, str(path))
    
    def parse_content(self, content: str, source_file: str = "") -> Graph:
        """
        Parse markdown content into a Graph.
        
        Args:
            content: Markdown content string.
            source_file: Source file path for reference.
            
        Returns:
            Graph containing all nodes and edges.
        """
        self.warnings = []
        graph = Graph(source_file=source_file)
        lines = content.split('\n')
        
        # Track parsing state
        current_node: Optional[Node] = None
        parent_stack: list[tuple[int, str]] = []  # (level, node_id)
        in_meta_block = False
        in_edges_block = False
        content_lines: list[str] = []
        edges_lines: list[str] = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            line_num = i + 1
            
            # Check for heading with ID
            heading_match = HEADING_PATTERN.match(line)
            if heading_match:
                # Save previous node's content
                if current_node:
                    current_node.content = '\n'.join(content_lines).strip()
                    content_lines = []
                
                # Parse heading
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                node_id = heading_match.group(3)
                
                # Check for duplicate ID
                if node_id in graph.nodes:
                    raise ParseError(f"Duplicate node ID: {node_id} (line {line_num})")
                
                # Determine parent from heading hierarchy
                parent_id = None
                while parent_stack and parent_stack[-1][0] >= level:
                    parent_stack.pop()
                if parent_stack:
                    parent_id = parent_stack[-1][1]
                
                # Create node
                current_node = Node(
                    id=node_id,
                    title=title,
                    level=level,
                    parent_id=parent_id,
                )
                graph.add_node(current_node)
                
                # Add to parent stack
                parent_stack.append((level, node_id))
                
                # Add parent-child edge if has parent
                if parent_id:
                    graph.add_edge(Edge(
                        source_id=parent_id,
                        target_id=node_id,
                        edge_type=EdgeType.PARENT_CHILD,
                    ))
                
                i += 1
                continue
            
            # Check for meta block start
            if META_START_PATTERN.match(line):
                in_meta_block = True
                i += 1
                continue
            
            # Parse meta lines
            if in_meta_block:
                meta_match = META_LINE_PATTERN.match(line)
                if meta_match and current_node:
                    key = meta_match.group(1).strip()
                    value = meta_match.group(2).strip()
                    self._apply_meta(current_node, key, value, line_num)
                    i += 1
                    continue
                else:
                    # End of meta block
                    in_meta_block = False
            
            # Check for edges block start
            if EDGES_START_PATTERN.match(line):
                in_edges_block = True
                edges_lines = []
                i += 1
                continue
            
            # Parse edges block
            if in_edges_block:
                if EDGES_END_PATTERN.match(line):
                    # Process edges
                    if current_node:
                        self._parse_edges(graph, current_node.id, edges_lines, line_num)
                    in_edges_block = False
                    edges_lines = []
                else:
                    edges_lines.append(line)
                i += 1
                continue
            
            # Collect content for current node
            if current_node and not in_meta_block and not in_edges_block:
                # Extract inline links as related edges (marked as inline links)
                for link_match in INLINE_LINK_PATTERN.finditer(line):
                    target_id = link_match.group(1)
                    graph.add_edge(Edge(
                        source_id=current_node.id,
                        target_id=target_id,
                        edge_type=EdgeType.RELATED,
                        is_inline_link=True,
                    ))
                
                content_lines.append(line)
            
            i += 1
        
        # Save last node's content
        if current_node:
            current_node.content = '\n'.join(content_lines).strip()
        
        # Validate graph
        validation_warnings = graph.validate()
        for warning in validation_warnings:
            self.warnings.append(ParseWarning(warning))
        
        # Remove edges with missing targets
        graph.edges = [
            e for e in graph.edges 
            if e.source_id in graph.nodes and e.target_id in graph.nodes
        ]
        
        return graph
    
    def _apply_meta(self, node: Node, key: str, value: str, line_num: int) -> None:
        """Apply a meta field to a node."""
        if key == "type":
            if self.config.validate_type(value):
                node.node_type = NodeType(value)
            else:
                self.warnings.append(ParseWarning(
                    f"Unknown type '{value}', using 'concept'", line_num
                ))
        
        elif key == "tags":
            tags = [t.strip() for t in value.split(',') if t.strip()]
            for tag in tags:
                if not self.config.validate_tag(tag):
                    self.warnings.append(ParseWarning(
                        f"Undefined tag '{tag}'", line_num
                    ))
            node.tags = tags
    
    def _parse_edges(self, graph: Graph, source_id: str, lines: list[str], line_num: int) -> None:
        """Parse edges from an edges block."""
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle YAML-like list format
            if line.startswith('- '):
                # This is a list item under a previous key
                continue
            
            match = EDGE_LINE_PATTERN.match(line)
            if match:
                edge_type_str = match.group(1).strip()
                targets_str = match.group(2).strip()
                
                # Map edge type
                edge_type_map = {
                    'prereqs': EdgeType.PREREQS,
                    'related': EdgeType.RELATED,
                    'contrasts': EdgeType.CONTRASTS,
                }
                
                if edge_type_str not in edge_type_map:
                    self.warnings.append(ParseWarning(
                        f"Unknown edge type '{edge_type_str}'", line_num
                    ))
                    continue
                
                edge_type = edge_type_map[edge_type_str]
                
                # Parse targets (comma-separated or YAML list)
                targets = [t.strip() for t in targets_str.split(',') if t.strip()]
                
                for target_id in targets:
                    # Clean up target ID
                    target_id = target_id.strip().lstrip('- ')
                    if target_id:
                        graph.add_edge(Edge(
                            source_id=source_id,
                            target_id=target_id,
                            edge_type=edge_type,
                        ))


def parse_markdown(file_path: str, config: Config) -> tuple[Graph, list[ParseWarning]]:
    """
    Convenience function to parse a markdown file.
    
    Args:
        file_path: Path to the markdown file.
        config: Configuration object.
        
    Returns:
        Tuple of (Graph, list of warnings).
    """
    parser = Parser(config)
    graph = parser.parse_file(file_path)
    return graph, parser.warnings

