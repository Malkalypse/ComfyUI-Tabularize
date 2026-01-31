# Changelog

All notable changes to ComfyUI-Tabularize will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-30

### Added
- Node organization system that arranges workflow nodes into columns based on connection topology
- Automatic link overlap detection and reroute point insertion
- Multi-component workflow support - detects and stacks disconnected workflow sections
- Intelligent vertical sorting based on child node input port positions
- Automatic cleanup of orphaned reroute points on re-organization
- Context menu integration with two commands:
  - "Tabularize - Organize Columns" - Arranges nodes and creates reroutes
  - "Tabularize - Reroute Links" - Analyzes and fixes link overlaps only
- Python backend API with action-based routing system
- Configurable layout constants (column spacing, row height, starting position)
- Smart column placement based on graph depth
- Direction optimization for reroute paths (up vs down)
- Component detection using depth-first search
- Component stacking (shortest to longest)
- Reroute management with automatic cleanup and ID reset
- Utility modules for debug logging (Python and JavaScript)

### Technical Details
- Action-based API dispatch table for extensibility
- Graph traversal algorithms for component detection and chain finding
- Coordinate-based collision detection for link overlap analysis
- Python and JavaScript logging integration for debugging

[1.0.0]: https://github.com/Malkalypse/ComfyUI-Tabularize/releases/tag/v1.0.0
