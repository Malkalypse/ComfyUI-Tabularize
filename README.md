# ComfyUI-Tabularize

Automatic node column organization and link routing for ComfyUI workflows.

## Features

### 🔲 Organize Columns
Automatically arranges your workflow nodes into clean, organized columns based on their connections:
- **Chain Detection**: Identifies linear node chains and organizes them horizontally
- **Column Layout**: Groups nodes into vertical columns based on their depth in the graph
- **Smart Spacing**: Maintains consistent spacing between nodes and columns
- **Preserved Connections**: All links remain intact during reorganization

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

1. Right-click on the canvas background
2. Select **🔲 Tabularize - Organize Columns** from the context menu
3. Your nodes will be automatically reorganized into columns
4. Links will automatically be rerouted to avoid overlaps

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

1. **Build Graph**: Creates parent/child relationship mapping from node connections
2. **Find Chains**: Identifies linear sequences of connected nodes
3. **Assign Columns**: Groups nodes by their depth in the dependency graph
4. **Calculate Positions**: Places nodes in columns with consistent spacing
5. **Apply Layout**: Updates node positions on the canvas

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
