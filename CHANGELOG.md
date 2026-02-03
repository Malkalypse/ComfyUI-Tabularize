# Changelog

All notable changes to ComfyUI-Tabularize will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-02-03

### Added
- Selected nodes organization support
  - When nodes are selected, only those nodes are organized
  - Selected nodes maintain their original top-left corner position after organization
  - Unselected nodes remain unchanged and unaffected
  - Node and link ID reindexing is skipped when organizing selected nodes (preserves IDs)
- Automatic node size normalization
  - All node sizes are rounded up to the nearest 10 units before organization
  - Example: A node with size [191, 245] becomes [200, 250]
  - Ensures consistent grid alignment and cleaner layouts
- Smart positioning based on organization scope
  - Selected nodes: Organized nodes maintain their original visual top-left corner
  - All nodes: Organized workflow starts at visual position [0, 0] (including title bar)
  - Uses node bounds (including title bars) for accurate visual positioning
- Shared utility functions
  - `getNodeBounds()` exported from `utils.js` for consistent node boundary calculations
  - Includes NODE_TITLE_BAR_HEIGHT constant for accurate positioning

### Changed
- ID reindexing now conditional based on organization scope
  - Full workflow organization: IDs are reindexed sequentially as before
  - Selected nodes organization: IDs are preserved to maintain references
- Position calculation improved to use visual bounds
  - Accounts for node title bar height in all position calculations
  - Ensures organized workflows align properly at [0, 0] without offset
- Backend filtering for selected nodes
  - Python backend receives `selectedNodeIds` array when nodes are selected
  - Filters nodes and links to only process selected subset
  - Returns positions only for the selected nodes

### Technical Details
- Selection detection in JavaScript checks `node.selected` property
- Frontend rounds node sizes before collecting graph data
- Backend calculates target position using `get_node_bounds()` for accurate corner detection
- Offset calculation aligns visual corners (including title bars) to target position
- Two-mode operation: full workflow vs. selected nodes subset

## [0.3.0] - 2026-02-02

### Added
- Automatic node ID reindexing after organization
  - Reindexes node IDs sequentially (1, 2, 3, ...) based on position
  - Sorts left-to-right by column, then top-to-bottom within columns
  - Uses two-pass algorithm to avoid ID conflicts during reindexing
  - Automatically updates all link references to maintain connections
- Automatic link ID reindexing after organization
  - Reindexes link IDs sequentially (1, 2, 3, ...) based on connection order
  - Sorts by origin node ID, then origin slot, then target node ID, then target slot
  - Uses two-pass algorithm to avoid ID conflicts during reindexing
  - Updates both graph links map and node input/output references
- Shared utility function `updateNodeID()` for consistent node ID updates
  - Exported from `utils.js` for reuse across multiple extensions
  - Handles graph registry updates and link reference updates

### Changed
- Organization workflow now includes automatic ID cleanup
  - Order: organize positions → reroute links → reindex nodes → reindex links
  - Results in clean, sequential IDs that match the visual layout
- Link reindexing ensures all node connections remain intact
  - Updates origin node output slot link arrays
  - Updates target node input slot link references

### Technical Details
- Two-pass reindexing strategy prevents ID collisions
  - First pass: reindex to temporary high IDs (max + 1, max + 2, ...)
  - Second pass: reindex to final sequential IDs (1, 2, 3, ...)
- Column detection uses 10px tolerance for grouping nodes
- Link sorting provides deterministic ordering for reproducible results

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

[0.4.0]: https://github.com/Malkalypse/ComfyUI-Tabularize/releases/tag/v0.4.0
[0.3.0]: https://github.com/Malkalypse/ComfyUI-Tabularize/releases/tag/v0.3.0
[0.2.0]: https://github.com/Malkalypse/ComfyUI-Tabularize/releases/tag/v0.2.0
[0.1.0]: https://github.com/Malkalypse/ComfyUI-Tabularize/releases/tag/v0.1.0
