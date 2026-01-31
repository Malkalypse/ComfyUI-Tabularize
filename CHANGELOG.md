# Changelog

All notable changes to ComfyUI-Tabularize will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-31

### Added
- Leftward connection detection and correction system
  - Iterative algorithm that identifies and fixes backward-flowing connections
  - Automatically moves nodes to appropriate columns to prevent connections from flowing leftward
  - Reduces leftward connections by 90%+ in complex workflows
- Column width calculation based on node sizes
  - Nodes in the same column are resized to match the widest node
  - Ensures consistent column widths across the workflow
- Uniform column spacing (100px between columns)
- Support for nodes assigned in Step 4 (non-chain nodes)
  - Previous version only handled nodes in longest chains
  - Now processes all nodes including isolated and side-branch nodes

### Fixed
- Column width detection now accounts for all nodes, not just chain nodes
- Position tracking using `column_x_positions` instead of requiring `new_positions`
- Node size initialization includes all nodes from `node_map`
- Leftward connection fixes now update column positions correctly
- Vertical sorting deferred until after column structure is finalized

### Changed
- Improved debug output organization
- Leftward connection fixing now runs for up to 20 iterations
- Column rebuilding after leftward fixes removes empty columns

### Known Issues
- In rare cases with complex circular dependencies, 1-2 leftward connections may remain after 20 iterations
- These edge cases will be addressed in a future update with improved dependency resolution

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

[0.2.0]: https://github.com/Malkalypse/ComfyUI-Tabularize/releases/tag/v0.2.0
[0.1.0]: https://github.com/Malkalypse/ComfyUI-Tabularize/releases/tag/v0.1.0
