"""
Command-line interface for the mind-map generator.

Provides commands to:
- generate: Convert markdown to Excalidraw
- sync-positions: Sync positions from edited Excalidraw file
- lint: Validate markdown against manifest rules
"""

import sys
from pathlib import Path
from typing import Optional

import click

from config import load_config
from parser import parse_markdown, ParseError
from graph import Graph
from layout import apply_layout
from positions import (
    load_positions, 
    save_positions, 
    apply_saved_positions,
    sync_positions_from_excalidraw
)
from excalidraw import save_excalidraw, get_excalidraw_path, estimate_node_dimensions


@click.group()
@click.version_option(version="0.1.0", prog_name="mindmap")
def cli():
    """Mind-Map: Convert markdown files to Excalidraw mind maps."""
    pass


@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True))
def generate(markdown_file: str):
    """
    Generate an Excalidraw file from a markdown file.
    
    Convention-based with zero configuration:
    - Output: <markdown_file>.excalidraw (same folder)
    - Config: config.yaml in same folder (or uses app defaults)
    - Positions: Auto-synced from excalidraw file if modified
    - Layout: Applied only to new nodes
    
    Example:
        mindmap generate atlas/sql/sql.md
        → Creates: atlas/sql/sql.excalidraw
        → Uses: atlas/sql/config.yaml (if exists)
    """
    try:
        md_path = Path(markdown_file)
        
        # Auto-detect project config (config.yaml in same folder)
        project_config = md_path.parent / "config.yaml"
        config_path = str(project_config) if project_config.exists() else None
        
        # Load configuration
        cfg = load_config(config_path)
        
        # Determine output path (same name, .excalidraw extension)
        output_path = str(get_excalidraw_path(markdown_file))
        excalidraw_path = Path(output_path)
        
        # Auto-sync positions from excalidraw file if it's newer than positions file
        positions_file = md_path.parent / f"{md_path.stem}.positions.json"
        if excalidraw_path.exists():
            excalidraw_mtime = excalidraw_path.stat().st_mtime
            positions_mtime = positions_file.stat().st_mtime if positions_file.exists() else 0
            
            if excalidraw_mtime > positions_mtime:
                # Excalidraw file was modified after positions file - sync it
                try:
                    sync_positions_from_excalidraw(str(excalidraw_path), markdown_file)
                    click.echo("✓ Synced positions from edited excalidraw file")
                except Exception as e:
                    click.echo(f"Warning: Could not sync positions: {e}", err=True)
        
        # Lint the markdown file
        click.echo("Validating markdown...")
        graph, warnings = parse_markdown(markdown_file, cfg)
        
        # Show warnings
        if warnings:
            for warning in warnings:
                click.echo(f"  Warning: {warning}", err=True)
        
        # Validate graph
        validation_errors = graph.validate()
        if validation_errors:
            for error in validation_errors:
                click.echo(f"  Error: {error}", err=True)
            click.echo("\n✗ Validation failed. Fix errors and try again.", err=True)
            sys.exit(1)
        
        click.echo(f"✓ Validated: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        
        # Load saved positions (includes width/height if saved)
        positions = load_positions(markdown_file)
        new_nodes = apply_saved_positions(graph, positions)
        
        # Estimate node dimensions based on content (only for nodes with default sizes)
        # This must run BEFORE layout so layout can use actual node sizes
        estimate_node_dimensions(graph, cfg)
        
        # Apply auto-layout only to new nodes (nodes without saved positions)
        # Uses actual node dimensions for proper spacing
        apply_layout(graph, cfg, new_nodes)
        
        # Save positions for next time
        save_positions(markdown_file, graph)
        
        # Generate Excalidraw file
        save_excalidraw(graph, cfg, output_path)
        
        click.echo(f"✓ Generated: {output_path}")
        
    except FileNotFoundError as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)
    except ParseError as e:
        click.echo(f"✗ Parse error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True))
def lint(markdown_file: str):
    """
    Validate a markdown file against manifest rules.
    
    Note: Linting is automatically performed during 'generate'.
    This command is for standalone validation without generation.
    
    Checks for:
    - Valid node IDs (globally unique, c-kebab-case)
    - Valid types (concept, example, code, table)
    - Defined tags (from config.yaml)
    - Valid edge references
    
    Example:
        mindmap lint atlas/sql/sql.md
    """
    try:
        md_path = Path(markdown_file)
        
        # Auto-detect project config
        project_config = md_path.parent / "config.yaml"
        config_path = str(project_config) if project_config.exists() else None
        
        # Load configuration
        cfg = load_config(config_path)
        
        # Parse markdown
        graph, warnings = parse_markdown(markdown_file, cfg)
        
        errors = []
        
        # Check node IDs
        for node in graph.nodes.values():
            if not node.id.startswith('c-'):
                errors.append(f"Node ID should start with 'c-': {node.id}")
        
        # Validate edges
        validation_errors = graph.validate()
        errors.extend(validation_errors)
        
        # Report results
        if warnings:
            click.echo("Warnings:")
            for warning in warnings:
                click.echo(f"  - {warning}")
        
        if errors:
            click.echo("\nErrors:")
            for error in errors:
                click.echo(f"  - {error}", err=True)
            click.echo(f"\n✗ Validation failed", err=True)
            sys.exit(1)
        else:
            click.echo(f"✓ {markdown_file} is valid")
            click.echo(f"  {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        
    except FileNotFoundError as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)
    except ParseError as e:
        click.echo(f"✗ Parse error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()

