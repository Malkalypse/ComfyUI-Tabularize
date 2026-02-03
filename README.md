# ComfyUI-Tabularize

Automatic node column organization and link routing for ComfyUI workflows.

## Features

### 🔲 Organize Columns
Automatically arranges your workflow nodes into clean, organized columns based on their connections:
- **Selected Nodes Support**: Organize only selected nodes while leaving others unchanged
- **Smart Positioning**: Selected nodes maintain their position; full workflows start at [0, 0]
- **Size Normalization**: Automatically rounds node sizes to nearest 10 units for grid alignment
- **Chain Detection**: Identifies linear node chains and organizes them horizontally
- **Column Layout**: Groups nodes into vertical columns based on their depth in the graph
- **Leftward Connection Prevention**: Automatically detects and corrects backward-flowing connections
- **Uniform Spacing**: Maintains consistent 100px spacing between columns
- **Consistent Sizing**: Nodes in the same column are sized to match the widest node
- **Smart Spacing**: Maintains consistent spacing between nodes vertically
- **Preserved Connections**: All links remain intact during reorganization
- **Conditional ID Cleanup**: Reindexes IDs for full workflows; preserves IDs for selected nodes

### 🔗 Reroute Links
Automatically detects and fixes overlapping links:
- **Overlap Detection**: Identifies links that pass through other nodes
- **Auto-Reroute**: Creates reroute points to route links around obstructing nodes
- **Clean Workflows**: Results in more readable and maintainable workflows

## Installation

1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/Malkalypse/ComfyUI-Tabularize.git
   ```

3. Restart ComfyUI

## Usage

### Organize Columns

**Organize All Nodes:**
1. Right-click on the canvas background (with no nodes selected)
2. Select **🔲 Tabularize - Organize Columns** from the context menu
3. All workflow nodes will be reorganized into columns starting at position [0, 0]
4. Node and link IDs will be reindexed sequentially
5. Links will automatically be rerouted to avoid overlaps

**Organize Selected Nodes:**
1. Select one or more nodes you want to organize
2. Right-click on the canvas background
3. Select **🔲 Tabularize - Organize Columns** from the context menu
4. Only the selected nodes will be reorganized, maintaining their original top-left position
5. Node and link IDs are preserved
6. Unselected nodes remain unchanged

### Reroute Links

1. Right-click on the canvas background
2. Select **🔗 Tabularize - Reroute Links** from the context menu
3. The extension will detect any links passing through nodes
4. Reroute points will be automatically added to route links cleanly

## How It Works

### Architecture

The extension uses a hybrid JavaScript/Python architecture:

- **JavaScript** ([tabularize.js](web/tabularize.js))
  - Collects graph data from the ComfyUI canvas
  - Sends data to Python backend via HTTP API
  - Applies position changes and creates reroute nodes
  - Adds context menu items to the canvas

- **Python** ([tabularize.py](tabularize.py))
  - Analyzes node graph structure
  - Calculates optimal column-based positions
  - Detects link-node intersections
  - Computes reroute point positions

- **API Layer** ([api.py](api.py))
  - Unified HTTP endpoint for all actions
  - Action-based dispatch with metadata
  - Error handling and logging

### Organization Algorithm

1. **Check Selection**: Detects if any nodes are selected to determine organization scope
2. **Normalize Sizes**: Rounds all node dimensions up to the nearest 10 units
3. **Filter Nodes**: If nodes are selected, filters to only those nodes and their interconnections
4. **Build Graph**: Creates parent/child relationship mapping from node connections
5. **Find Chains**: Identifies linear sequences of connected nodes
6. **Assign Columns**: Groups nodes by their depth in the dependency graph
7. **Fix Leftward Connections**: Iteratively detects and corrects backward-flowing links
   - Analyzes all connections to find those flowing leftward
   - Moves target nodes to columns after their origins
   - Recalculates column widths after each adjustment
   - Runs up to 20 iterations to resolve complex dependencies
8. **Rebuild Columns**: Removes empty columns and recalculates widths
9. **Match Widths**: Resizes nodes to match their column's maximum width
10. **Apply Uniform Spacing**: Positions columns with consistent 100px gaps
11. **Vertical Sort**: Arranges nodes within columns based on port connections
12. **Apply Position Offset**: Aligns organized nodes to target position
    - Selected nodes: Maintains original top-left corner position
    - All nodes: Aligns workflow to visual position [0, 0]
13. **Apply Layout**: Updates node positions on the canvas
14. **Reroute Links**: Automatically detects and fixes overlapping links
15. **Reindex Node IDs** (full workflow only): Sequentially renumbers nodes (1, 2, 3, ...) based on position
    - Sorts left-to-right by column, top-to-bottom within columns
    - Uses two-pass algorithm to prevent ID conflicts
    - Skipped when organizing selected nodes to preserve references
16. **Reindex Link IDs** (full workflow only): Sequentially renumbers links (1, 2, 3, ...) based on connections
    - Sorts by origin node, origin slot, target node, target slot
    - Maintains all node input/output references
    - Skipped when organizing selected nodes to preserve references

### Reroute Algorithm

1. **Collect Links**: Gathers all connections between nodes
2. **Detect Overlaps**: Checks which links pass through node bounding boxes
3. **Calculate Points**: Determines reroute positions around obstructing nodes
4. **Create Reroutes**: Adds LiteGraph reroute nodes at calculated positions

## Development

### Project Structure

```
ComfyUI-Tabularize/
├── __init__.py          # Package initialization, loads API routes
├── api.py               # HTTP API handlers with action dispatch
├── tabularize.py        # Core organization and routing algorithms
├── utils.py             # Python utility functions (debug logging)
├── LICENSE              # MPL-2.0 license
├── CHANGELOG.md         # Version history
├── README.md            # This file
├── pyproject.toml       # Project metadata
└── web/
    ├── tabularize.js    # Frontend extension and UI integration
    └── utils.js         # JavaScript utility functions (logging, debug)
```

### API Reference

#### Endpoint: `/tabularize/action`

**Log Action**
```json
{
  "action": "log",
  "message": "Your log message"
}
```

**Organize Action**
```json
{
  "action": "organize",
  "graph": {
    "nodes": [...],
    "links": [...]
  }
}
```

**Reroute Action**
```json
{
  "action": "reroute",
  "graph": {
    "nodes": [...],
    "links": [...]
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MPL-2.0 License - See LICENSE file for details

## Credits

Created for the ComfyUI community to help manage complex workflow layouts.
