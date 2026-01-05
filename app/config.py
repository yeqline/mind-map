"""
Configuration loading and validation.

This module handles loading config.yaml files and provides
validated configuration objects for styling nodes and edges.
"""

import os
from dataclasses import dataclass, field, fields, MISSING
from pathlib import Path
from typing import Optional, Any, TypeVar

import yaml

from graph import NodeType, EdgeType

T = TypeVar('T')


def _merge_dataclass(dataclass_type: type[T], yaml_data: dict, base_instance: Optional[T] = None) -> T:
    """
    Generic function to merge YAML data into a dataclass instance.
    
    Args:
        dataclass_type: The dataclass type to instantiate
        yaml_data: Dictionary of values from YAML
        base_instance: Optional base instance to merge with (for property-level overrides)
    
    Returns:
        New instance of dataclass_type with merged values
    
    Example:
        # Default instance has: fill="#e3f2fd", stroke="#1976d2"
        # YAML has: {"fill": "yellow"}
        # Result: fill="yellow", stroke="#1976d2" (from base)
    """
    kwargs = {}
    
    for field_info in fields(dataclass_type):
        field_name = field_info.name
        
        # Priority order:
        # 1. Value from yaml_data (if present)
        # 2. Value from base_instance (if provided)
        # 3. Default value from dataclass field
        
        if field_name in yaml_data:
            # Use value from YAML
            kwargs[field_name] = yaml_data[field_name]
        elif base_instance is not None:
            # Use value from base instance
            kwargs[field_name] = getattr(base_instance, field_name)
        elif field_info.default is not MISSING:
            # Use default value
            kwargs[field_name] = field_info.default
        elif field_info.default_factory is not MISSING:
            # Use default factory
            kwargs[field_name] = field_info.default_factory()
        # else: field is required and will raise error if not provided
    
    return dataclass_type(**kwargs)


@dataclass
class NodeStyle:
    """Visual style for a node type."""
    fill: str = "#e3f2fd"
    stroke: str = "#1976d2"
    stroke_width: int = 2
    font_family: int = 1  # 1=Virgil, 2=Helvetica, 3=Cascadia
    font_size: int = 20
    border_radius: int = 8
    padding: int = 16


@dataclass
class EdgeStyle:
    """Visual style for an edge type."""
    stroke: str = "#666666"
    stroke_width: int = 2
    stroke_style: str = "solid"  # solid | dashed | dotted
    start_arrowhead: Optional[str] = None
    end_arrowhead: Optional[str] = "arrow"


@dataclass
class TagStyle:
    """Visual style for a tag."""
    color: str = "#2196f3"


@dataclass
class LayoutConfig:
    """Layout configuration."""
    node_width: int = 250
    node_min_height: int = 80
    horizontal_gap: int = 120
    vertical_gap: int = 100
    auto_layout: str = "tree"  # tree | force | none


@dataclass
class Config:
    """
    Complete configuration for mind-map generation.
    
    Attributes:
        node_types: Mapping of NodeType to NodeStyle
        edge_types: Mapping of EdgeType to EdgeStyle
        tags: Mapping of tag name to TagStyle
        layout: Layout configuration
    """
    node_types: dict[NodeType, NodeStyle] = field(default_factory=dict)
    edge_types: dict[EdgeType, EdgeStyle] = field(default_factory=dict)
    tags: dict[str, TagStyle] = field(default_factory=dict)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    
    def get_node_style(self, node_type: NodeType) -> NodeStyle:
        """Get style for a node type, with fallback to concept style."""
        return self.node_types.get(node_type, self.node_types.get(NodeType.CONCEPT, NodeStyle()))
    
    def get_edge_style(self, edge_type: EdgeType) -> EdgeStyle:
        """Get style for an edge type, with fallback to parent_child style."""
        return self.edge_types.get(edge_type, self.edge_types.get(EdgeType.PARENT_CHILD, EdgeStyle()))
    
    def get_tag_color(self, tag: str) -> Optional[str]:
        """Get color for a tag, or None if tag is undefined."""
        tag_style = self.tags.get(tag)
        return tag_style.color if tag_style else None
    
    def validate_tag(self, tag: str) -> bool:
        """Check if a tag is defined in the config."""
        return tag in self.tags
    
    def validate_type(self, type_str: str) -> bool:
        """Check if a type string is valid."""
        try:
            NodeType(type_str)
            return True
        except ValueError:
            return False


def _parse_node_style(data: dict, base_style: Optional[NodeStyle] = None) -> NodeStyle:
    """
    Parse a node style from YAML data, merging with base style if provided.
    
    Args:
        data: YAML data dictionary
        base_style: Optional base style to merge with (for property-level overrides)
    
    Returns:
        NodeStyle with merged properties
    """
    return _merge_dataclass(NodeStyle, data, base_style)


def _parse_edge_style(data: dict, base_style: Optional[EdgeStyle] = None) -> EdgeStyle:
    """
    Parse an edge style from YAML data, merging with base style if provided.
    
    Args:
        data: YAML data dictionary
        base_style: Optional base style to merge with (for property-level overrides)
    
    Returns:
        EdgeStyle with merged properties
    """
    return _merge_dataclass(EdgeStyle, data, base_style)


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from a YAML file with granular property-level merging.
    
    The config system works in layers:
    1. Default config (app/default_config.yaml) is loaded first
    2. If config_path is provided, it's loaded and merged at the property level
    3. Project config values override only the specific properties they define
    
    Example:
        Default has: concept.fill="#e3f2fd", concept.stroke="#1976d2"
        Project has: concept.fill="yellow"
        Result: concept.fill="yellow", concept.stroke="#1976d2" (from default)
    
    Args:
        config_path: Path to config.yaml. If None, uses only default config.
        
    Returns:
        Validated Config object with merged properties.
        
    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config is invalid.
    """
    config = Config()
    
    # Load default config first
    default_path = Path(__file__).parent / "default_config.yaml"
    if default_path.exists():
        with open(default_path) as f:
            default_data = yaml.safe_load(f) or {}
        _apply_config_data(config, default_data)
    
    # Load custom config if provided
    if config_path:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path) as f:
            custom_data = yaml.safe_load(f) or {}
        _apply_config_data(config, custom_data)
    
    # Ensure all node types have styles
    for node_type in NodeType:
        if node_type not in config.node_types:
            config.node_types[node_type] = NodeStyle()
    
    # Ensure all edge types have styles
    for edge_type in EdgeType:
        if edge_type not in config.edge_types:
            config.edge_types[edge_type] = EdgeStyle()
    
    return config


def _apply_config_data(config: Config, data: dict) -> None:
    """
    Apply YAML data to a Config object, merging properties at a granular level.
    
    This allows project configs to override only specific properties while
    keeping other properties from the default config.
    """
    # Parse node types (merge at property level)
    if "node_types" in data:
        for type_name, style_data in data["node_types"].items():
            try:
                node_type = NodeType(type_name)
                # Get existing style if present (for merging)
                base_style = config.node_types.get(node_type)
                config.node_types[node_type] = _parse_node_style(style_data or {}, base_style)
            except ValueError:
                pass  # Skip unknown types
    
    # Parse edge types (merge at property level)
    if "edge_types" in data:
        for type_name, style_data in data["edge_types"].items():
            try:
                edge_type = EdgeType(type_name)
                # Get existing style if present (for merging)
                base_style = config.edge_types.get(edge_type)
                config.edge_types[edge_type] = _parse_edge_style(style_data or {}, base_style)
            except ValueError:
                pass  # Skip unknown types
    
    # Parse tags (additive: new tags are added to existing ones)
    if "tags" in data and data["tags"]:
        for tag_name, tag_data in data["tags"].items():
            if tag_data:
                config.tags[tag_name] = TagStyle(color=tag_data.get("color", "#2196f3"))
    
    # Parse layout (merge at property level)
    if "layout" in data:
        config.layout = _merge_dataclass(LayoutConfig, data["layout"], config.layout)

