'''
Tabularize - Node organization logic
All graph processing happens here in Python
'''

from .utils import set_debug
DEBUG_LEVEL = 0
debug = set_debug( DEBUG_LEVEL )


def line_segment_intersects_rect(
    x1, y1,
    x2, y2,
    rect_x, rect_y,
    rect_w, rect_h
):
    '''
    Check if a line segment intersects with a rectangle.
    
    Args:
        x1, y1:         start point of line
        x2, y2:         end point of line
        rect_x, rect_y: top-left corner of rectangle
        rect_w, rect_h: width and height of rectangle
        
    Returns:
        True if line intersects rectangle, False otherwise
    '''

    # Check if either endpoint is inside the rectangle
    def point_in_rect( px, py ):
        return(
            rect_x <= px <= rect_x + rect_w and 
            rect_y <= py <= rect_y + rect_h
        )
    
    # If either endpoint is inside the rectangle, the line intersects
    if point_in_rect( x1, y1 ) or point_in_rect( x2, y2 ):
        return True

    def line_segments_intersect( ax1, ay1, ax2, ay2, bx1, by1, bx2, by2 ):
        '''Check if two line segments intersect'''
        def ccw( ax, ay, bx, by, cx, cy ):
            return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
        
        a = ccw( ax1, ay1, bx1, by1, bx2, by2 )
        b = ccw( ax2, ay2, bx1, by1, bx2, by2 )
        c = ccw( ax1, ay1, ax2, ay2, bx1, by1 )
        d = ccw( ax1, ay1, ax2, ay2, bx2, by2 )
        
        return a != b and c != d
    
    # Four edges of the rectangle
    edges = [
        (rect_x, rect_y, rect_x + rect_w, rect_y),                   # top
        (rect_x + rect_w, rect_y, rect_x + rect_w, rect_y + rect_h), # right
        (rect_x, rect_y + rect_h, rect_x + rect_w, rect_y + rect_h), # bottom
        (rect_x, rect_y, rect_x, rect_y + rect_h)                    # left
    ]
    
    # Check if the line intersects any of the rectangle's edges
    for edge_x1, edge_y1, edge_x2, edge_y2 in edges:
        if line_segments_intersect(
            x1, y1, x2, y2, edge_x1, edge_y1, edge_x2, edge_y2
        ):
            return True
    
    return False

def build_node_graph( nodes, links):
    '''
    Build a graph representation showing node connections
    
    Returns:
        node_map: dict mapping node_id -> node data
        children: dict mapping node_id -> list of child node_ids
        parents:  dict mapping node_id -> list of parent node_ids
    '''

    node_map = {node['id']: node for node in nodes}
    children = {node['id']: [] for node in nodes}
    parents  = {node['id']: [] for node in nodes}
    
    for link in links:
        origin_id = link['origin_id']
        target_id = link['target_id']
        
        if origin_id in children and target_id in parents:
            children[origin_id].append( target_id )
            parents[target_id].append( origin_id )
    
    return node_map, children, parents


def find_all_chains( node_map, children, parents ):
    '''
    Find all chains from start nodes (no inputs) to end nodes (no outputs)
    
    Returns:
        List of chains, where each chain is a list of node_ids
    '''
    
    # Find start nodes (nodes with no parents/inputs)
    start_nodes = [node_id for node_id, parent_list in parents.items() if len( parent_list ) == 0]


def find_disconnected_components( nodes, links ):
    '''
    Find disconnected components (separate workflows) in the graph.
    
    Returns:
        List of components, where each component is a list of node_ids
    '''
    node_ids = {node['id'] for node in nodes}
    
    # Build adjacency for undirected graph (connections in both directions)
    adjacency = {node_id: set() for node_id in node_ids}
    for link in links:
        origin_id = link['origin_id']
        target_id = link['target_id']
        if origin_id in adjacency and target_id in adjacency:
            adjacency[origin_id].add( target_id )
            adjacency[target_id].add( origin_id )
    
    # Find connected components using DFS
    visited = set()
    components = []
    
    def dfs( node_id, component ):
        visited.add( node_id )
        component.append( node_id )
        for neighbor in adjacency[node_id]:
            if neighbor not in visited:
                dfs( neighbor, component )
    
    for node_id in node_ids:
        if node_id not in visited:
            component = []
            dfs( node_id, component )
            components.append( component )
    
    return components


def find_all_chains( node_map, children, parents ):
    '''
    Find all chains from start nodes (no inputs) to end nodes (no outputs)
    
    Returns:
        List of chains, where each chain is a list of node_ids
    '''
    
    # Find start nodes (nodes with no parents/inputs)
    start_nodes = [node_id for node_id, parent_list in parents.items() if len( parent_list ) == 0]
    
    debug( f'\n✓ Found {len( start_nodes )} start nodes (no inputs)')
    for node_id in start_nodes:
        node = node_map[node_id]
        debug( f'  - {node["type"]} (ID: {node_id})' )
    
    # Build all chains using DFS from each start node
    all_chains = []
    
    def dfs_build_chains( current_id, current_chain ):
        '''Recursively build chains from current node'''
        
        current_chain = current_chain + [current_id]
        
        # Get children of current node
        node_children = children.get( current_id, [] )
        
        if len( node_children ) == 0:
            # This is an end node (no outputs), save the chain
            all_chains.append( current_chain )
        else:
            # Continue building chains through each child
            for child_id in node_children:
                dfs_build_chains( child_id, current_chain )
    
    # Start DFS from each start node
    for start_id in start_nodes:
        dfs_build_chains( start_id, [] )
    
    return all_chains


def organize_nodes( graph_data ):
    '''
    Main function to organize nodes into columns
    
    Args:
        graph_data: Dictionary containing nodes and links from the graph
        
    Returns:
        Dictionary with new positions for each node
    '''
    
    debug( '\n' + '='*50 )
    debug( 'TABULARIZE - Organizing Workflow Nodes')
    debug( '='*50 )
    
    all_nodes = graph_data.get( 'nodes', [] )
    links = graph_data.get( 'links', [] )
    
    debug( f'✓ Received {len( all_nodes )} total nodes and {len( links )} links' )
    
    # Filter to only workflow nodes (nodes that have inputs or outputs with connections)
    # Exclude notes, text, groups, and other non-workflow elements
    connected_node_ids = set()
    for link in links:
        connected_node_ids.add( link['origin_id'] )
        connected_node_ids.add( link['target_id'] )
    
    # Only process nodes that are connected via links
    nodes = [node for node in all_nodes if node['id'] in connected_node_ids]
    
    excluded_count = len(all_nodes) - len(nodes)
    if excluded_count > 0:
        debug( f'✓ Filtering: {len( nodes )} connected workflow nodes, {excluded_count} unconnected elements excluded' )
    
    if not nodes:
        print( 'No connected workflow nodes found.' )
        return {
            'status':    'success',
            'message':   'No workflow nodes to organize',
            'positions': {}
        }
    
    # Find disconnected components (separate workflows)
    components = find_disconnected_components( nodes, links )
    
    debug( f'\n✓ Found {len( components )} disconnected component(s)' )
    
    if len( components ) == 1:
        # Single component - organize normally
        return organize_single_component( nodes, links, 0 )
    
    else:
        # Multiple components - organize each separately and stack vertically
        debug( '\nProcessing multiple components separately...' )
        
        # Organize each component and calculate its layout bounds
        component_results = []
        
        for i, component_node_ids in enumerate( components ):
            debug( f'\n--- Component {i+1}/{len(components)} with {len(component_node_ids)} nodes ---' )
            
            # Filter nodes and links for this component
            component_nodes = [n for n in nodes if n['id'] in component_node_ids]
            component_links = [l for l in links if l['origin_id'] in component_node_ids and l['target_id'] in component_node_ids]
            
            # Organize this component
            result = organize_single_component( component_nodes, component_links, 0 )
            
            if result['status'] == 'success' and result['positions']:
                # Calculate bounding box height
                max_y = max( pos[1] + [n for n in component_nodes if n['id'] == nid][0]['size'][1] 
                            for nid, pos in result['positions'].items() )
                min_y = min( pos[1] for pos in result['positions'].values() )
                height = max_y - min_y
                
                component_results.append( {
                    'positions': result['positions'],
                    'sizes': result['sizes'],
                    'height': height,
                    'node_count': len(component_node_ids)
                } )
        
        # Sort components by height (shortest first)
        component_results.sort( key=lambda c: c['height'] )
        
        debug( f'\n\nStacking {len(component_results)} components (shortest to longest)' )
        
        # Stack components vertically
        all_positions = {}
        all_sizes = {}
        current_y_offset = 0
        component_spacing = 200  # Vertical spacing between components
        
        for i, comp in enumerate( component_results ):
            debug( f'\nComponent {i+1}: height={comp["height"]:.0f}, nodes={comp["node_count"]}' )
            
            # Find minimum Y in this component
            min_y = min( pos[1] for pos in comp['positions'].values() )
            
            # Adjust all positions with offset
            for node_id, pos in comp['positions'].items():
                adjusted_y = pos[1] - min_y + current_y_offset
                all_positions[node_id] = [pos[0], adjusted_y]
                debug( f'  Node {node_id}: Y {pos[1]:.0f} -> {adjusted_y:.0f}' )
            
            # Copy sizes
            all_sizes.update( comp['sizes'] )
            
            # Update offset for next component
            current_y_offset += comp['height'] + component_spacing
        
        debug( f'\n✓ Stacked {len(component_results)} components' )
        debug( '='*50 )
        debug( '' )
        
        return {
            'status':    'success',
            'message':   f'Complete - positioned {len(all_positions)} nodes in {len(component_results)} components',
            'positions': all_positions,
            'sizes':     all_sizes
        }


def organize_single_component( nodes, links, start_y ):
    '''
    Organize a single connected component into columns
    
    Args:
        nodes: List of node dictionaries for this component
        links: List of link dictionaries for this component
        start_y: Starting Y position for this component
        
    Returns:
        Dictionary with positions and sizes for nodes in this component
    '''
    
    if not nodes:
        return {
            'status':    'success',
            'message':   'No nodes to organize',
            'positions': {},
            'sizes':     {}
        }
    
    # Build graph representation
    node_map, children, parents = build_node_graph( nodes, links )
    
    # Find all chains
    chains = find_all_chains( node_map, children, parents )
    
    debug( f'✓ Found {len( chains )} chains from start to end' )
    
    # Find longest chain(s)
    if not chains:
        print( '⚠ No complete chains found (nodes may be isolated or circular)' )
        return {
            'status':    'success',
            'message':   'No chains to organize',
            'positions': {}
        }
    
    # Find the longest chain(s)
    max_length     = max( len( chain ) for chain in chains )
    longest_chains = [chain for chain in chains if len( chain ) == max_length]
    
    debug( f'\n✓ Longest chain length: {max_length} nodes' )
    debug( f'✓ Number of longest chains: {len( longest_chains )}' )
    
    # Layout configuration
    START_X        = 100  # Starting X position
    COLUMN_SPACING = 100  # Extra spacing between columns
    ROW_HEIGHT     = 150  # Vertical spacing between chains
    
    # First pass: determine which nodes go in which columns and track max width per column
    column_nodes  = {}  # column_idx -> list of node_ids
    column_widths = {}  # column_idx -> max width
    
    # Assign nodes to columns based on their position in the longest chains
    for chain in longest_chains:
        for col_idx, node_id in enumerate(chain):
            if col_idx not in column_nodes:
                column_nodes[col_idx]  = []
                column_widths[col_idx] = 0
            
            if node_id not in column_nodes[col_idx]:
                column_nodes[col_idx].append( node_id )
                node_width = node_map[node_id]['size'][0]
                column_widths[col_idx] = max( column_widths[col_idx], node_width )
    
    # Calculate X positions for each column based on cumulative widths
    column_x_positions = {}
    current_x          = START_X
    
    debug( '\nColumn layout:' )
    for col_idx in sorted( column_widths.keys() ):
        column_x_positions[col_idx] = current_x
        debug( f'  Column {col_idx}: X={current_x}, Max Width={column_widths[col_idx]}' )
        current_x += column_widths[col_idx] + COLUMN_SPACING
    
    # Assign positions to nodes in longest chains
    positioned_nodes = set()
    new_positions    = {}
    
    debug( '\nArranging longest chains:' )
    for chain_idx, chain in enumerate(longest_chains):
        debug( f'\n  Chain {chain_idx + 1}:' )
        y_pos = start_y + (chain_idx * ROW_HEIGHT)
        
        for col_idx, node_id in enumerate(chain):
            if node_id not in positioned_nodes:
                x_pos = column_x_positions[col_idx]
                new_positions[node_id] = [x_pos, y_pos]
                positioned_nodes.add( node_id )
                
                node = node_map[node_id]
                debug( f'    Column {col_idx}: {node["type"]}({node_id}) width={node["size"][0]} -> [{x_pos}, {y_pos}]' )
            else:
                # Node already positioned (shared between chains)
                existing_pos = new_positions[node_id]
                node = node_map[node_id]
                debug( f'    Column {col_idx}: {node["type"]}({node_id}) -> already at {existing_pos}' )
    
    debug( f'\n✓ Positioned {len( new_positions )} nodes from longest chains' )
    unpositioned_count = len(nodes) - len(new_positions)
    debug( f'✓ {unpositioned_count} nodes remain unpositioned' )
    
    # Step 4: Position remaining nodes (column assignment only)
    if unpositioned_count > 0:
        debug( '\n' + '-'*50 )
        debug( 'Step 4: Assigning columns for remaining nodes' )
        debug( '-'*50 )
        
        # Create reverse mapping: position -> column index
        pos_to_column = {}
        for col_idx in column_x_positions:
            pos_to_column[column_x_positions[col_idx]] = col_idx
        
        # Track which nodes are positioned and their columns
        node_columns = {}  # node_id -> column_idx
        for node_id, pos in new_positions.items():
            x_pos = pos[0]
            if x_pos in pos_to_column:
                node_columns[node_id] = pos_to_column[x_pos]
        
        # Find unpositioned nodes
        unpositioned_nodes = [node_id for node_id in node_map.keys() if node_id not in positioned_nodes]
        
        debug( f'\nProcessing {len( unpositioned_nodes )} unpositioned nodes:' )
        
        for node_id in unpositioned_nodes:
            node          = node_map[node_id]
            target_column = None
            
            # Check if node has positioned children (nodes it outputs to)
            positioned_children = [child_id for child_id in children.get( node_id, [] ) if child_id in node_columns]
            
            # Check if node has positioned parents (nodes it receives input from)
            positioned_parents = [parent_id for parent_id in parents.get(node_id, []) if parent_id in node_columns]
            
            # Determine column placement
            if positioned_parents:
                # Place in column after the last (rightmost) positioned parent
                parent_columns = [node_columns[pid] for pid in positioned_parents]
                max_parent_col = max( parent_columns )
                target_column  = max_parent_col + 1
                debug( f'  {node["type"]}({node_id}): Has parents in columns {parent_columns} -> placing in column {target_column}' )

            elif positioned_children:
                # Place in column before the first (leftmost) positioned child
                child_columns = [node_columns[cid] for cid in positioned_children]
                min_child_col = min( child_columns )
                target_column = min_child_col - 1
                debug( f'  {node["type"]}({node_id}): Has children in columns {child_columns} -> placing in column {target_column}' )

            else:
                # Node is isolated or only connects to other unpositioned nodes
                # Place it in a new column at the end
                target_column = max( column_x_positions.keys()) + 1 if column_x_positions else 0
                debug( f'  {node["type"]}({node_id}): Isolated -> placing in new column {target_column}' )
            
            # Ensure column exists
            if target_column not in column_x_positions:
                
                # Create new column
                if column_x_positions:
                    last_col   = max( column_x_positions.keys() )
                    last_x     = column_x_positions[last_col]
                    last_width = column_widths[last_col]
                    new_x      = last_x + last_width + COLUMN_SPACING
                else:
                    new_x = START_X
                
                column_x_positions[target_column] = new_x
                column_widths[target_column] = node['size'][0]
                debug( f'    Created new column {target_column} at X={new_x}' )
            else:
                # Update column width if this node is wider
                column_widths[target_column] = max( column_widths[target_column], node['size'][0] )
            
            # Store column assignment (Y position will be determined in Step 5)
            node_columns[node_id] = target_column
            positioned_nodes.add( node_id )
            debug( f'    Assigned to column {target_column}' )
    else:
        # Create node_columns mapping for already positioned nodes
        pos_to_column = {}
        for col_idx in column_x_positions:
            pos_to_column[column_x_positions[col_idx]] = col_idx
        
        node_columns = {}
        for node_id, pos in new_positions.items():
            x_pos = pos[0]
            if x_pos in pos_to_column:
                node_columns[node_id] = pos_to_column[x_pos]
    
    # Step 5: Sort nodes vertically within each column based on connected ports
    debug( '\n' + '-'*50 )
    debug( 'Step 5: Sorting nodes vertically by port connections' )
    debug( '-'*50 )
    
    NODE_VERTICAL_SPACING = 60  # Spacing between nodes in same column (accounts for 30px title bar)
    PORT_SPACING          = 20  # Estimated spacing between ports on a node
    
    def calculate_port_y( node_id, slot_index, is_output=True ):
        '''Calculate estimated Y position of a port on a node'''

        if node_id not in new_positions:
            return 0
        
        node_y = new_positions[node_id][1]

        # Ports start with some offset from top of node
        port_offset = 30 + (slot_index * PORT_SPACING)
        return node_y + port_offset
    
    def get_connected_port_positions( node_id ):
        '''Get Y positions of all ports this node connects to, sorted by Y'''
        
        port_positions = []
        
        # Check parent connections (input ports)
        for link in links:
            if link['target_id'] == node_id:
                parent_id   = link['origin_id']
                origin_slot = link['origin_slot']

                if parent_id in new_positions:
                    port_y = calculate_port_y( parent_id, origin_slot, is_output=True )
                    port_positions.append( port_y )
        
        # Check child connections (output ports)
        for link in links:
            if link['origin_id'] == node_id:
                child_id    = link['target_id']
                target_slot = link['target_slot']

                if child_id in new_positions:
                    port_y = calculate_port_y( child_id, target_slot, is_output=False )
                    port_positions.append( port_y )
        
        return sorted( port_positions )
    
    # Group nodes by column
    columns_to_nodes = {}  # column_idx -> list of node_ids
    for node_id, col_idx in node_columns.items():
        if col_idx not in columns_to_nodes:
            columns_to_nodes[col_idx] = []
        columns_to_nodes[col_idx].append(node_id)
    
    # Sort and position nodes in each column
    new_positions = {}
    
    for col_idx in sorted( columns_to_nodes.keys() ):
        nodes_in_column = columns_to_nodes[col_idx]
        x_pos           = column_x_positions[col_idx]
        
        debug( f'\nColumn {col_idx} (X={x_pos}): {len(nodes_in_column)} nodes' )
        
        # Sort nodes by their connected port positions
        def sort_key( node_id ):
            port_positions = get_connected_port_positions( node_id )

            # Return tuple of port positions for sorting (ties broken by subsequent ports)
            # Pad with infinity so nodes with fewer connections sort last
            return port_positions + [float( 'inf' )] * 10 if port_positions else [float( 'inf' )] * 10
        
        sorted_nodes = sorted( nodes_in_column, key=sort_key )
        
        # Position nodes vertically
        current_y = start_y
        
        for node_id in sorted_nodes:
            node           = node_map[node_id]
            node_height    = node['size'][1]
            port_positions = get_connected_port_positions( node_id )
            
            new_positions[node_id] = [x_pos, current_y]
            
            port_str = f'ports at {port_positions}' if port_positions else 'no connections'
            debug( f'  {node["type"]}({node_id}): {port_str} -> Y={current_y}' )
            
            current_y += node_height + NODE_VERTICAL_SPACING
    
    debug( f'\n✓ All {len( nodes )} nodes positioned with proper vertical sorting' )
    
    # Step 5b: Re-sort first column based on second column's input port positions
    if 0 in columns_to_nodes and 1 in columns_to_nodes:
        debug( '\n' + '-'*50 )
        debug( 'Step 5b: Re-sorting first column based on child port positions' )
        debug( '-'*50 )
        
        first_column_nodes = columns_to_nodes[0]
        
        def get_child_input_port_positions( node_id ):
            '''Get Y positions of child nodes' input ports that this node connects to'''
            port_positions = []
            
            for link in links:
                if link['origin_id'] == node_id:
                    child_id    = link['target_id']
                    target_slot = link['target_slot']
                    
                    if child_id in new_positions:
                        port_y = calculate_port_y( child_id, target_slot, is_output=False )
                        port_positions.append( port_y )
            
            return sorted( port_positions )
        
        # Sort first column nodes by their children's input port positions
        def first_col_sort_key( node_id ):
            port_positions = get_child_input_port_positions( node_id )
            return port_positions + [float('inf')] * 10 if port_positions else [float('inf')] * 10
        
        sorted_first_col = sorted( first_column_nodes, key=first_col_sort_key )
        
        # Re-position first column nodes
        x_pos     = column_x_positions[0]
        current_y = start_y
        
        debug( f'\nColumn 0 (X={x_pos}): Re-positioning {len(sorted_first_col)} nodes' )
        
        for node_id in sorted_first_col:
            node           = node_map[node_id]
            node_height    = node['size'][1]
            port_positions = get_child_input_port_positions( node_id )
            
            new_positions[node_id] = [x_pos, current_y]
            
            port_str = f'child ports at {port_positions}' if port_positions else 'no connections'
            debug( f'  {node["type"]}({node_id}): {port_str} -> Y={current_y}' )
            
            current_y += node_height + NODE_VERTICAL_SPACING
        
        debug( f'\n✓ First column re-sorted based on child connections' )
    
    # Adjust node widths to match column width
    debug( '\n' + '-'*50 )
    debug( '\nStep 3b: Matching node widths within columns' )
    debug( '-'*50 )
    
    node_sizes = {}  # node_id -> [width, height]
    
    for col_idx in sorted( columns_to_nodes.keys() ):
        nodes_in_column = columns_to_nodes[col_idx]
        column_width    = column_widths[col_idx]
        
        debug( f'Column {col_idx}: Setting all nodes to width {column_width}' )
        
        for node_id in nodes_in_column:
            node                = node_map[node_id]
            original_width      = node['size'][0]
            node_sizes[node_id] = [column_width, node['size'][1]]
            
            if original_width != column_width:
                debug( f'  {node["type"]}({node_id}): {original_width} -> {column_width}' )
    
    debug( f'\n✓ Adjusted widths for {len(node_sizes)} nodes' )
    debug( '='*50 )
    debug( '' )
    
    return {
        'status':    'success',
        'message':   f'Complete - positioned {len(new_positions)} nodes',
        'positions': new_positions,
        'sizes':     node_sizes
    }


def detect_link_overlaps( graph_data ):
    '''
    Detect which links pass behind nodes (overlap detection).
    Step 1: Identify overlapping links.
    
    Args:
        graph_data: Dictionary containing nodes and links from the graph
        
    Returns:
        Dictionary with information about overlapping links
    '''

    debug( '\n' + '='*50 )
    debug( 'REROUTE LINKS - Step 1: Detecting Overlaps' )
    debug( '='*50 )
    
    all_nodes = graph_data.get( 'nodes', [] )
    links     = graph_data.get( 'links', [] )
    
    debug( f'✓ Analyzing {len( links )} links against {len( all_nodes )} total nodes' )
    
    # Filter to only workflow nodes (nodes that have connections)
    connected_node_ids = set()
    for link in links:
        connected_node_ids.add( link['origin_id'] )
        connected_node_ids.add( link['target_id'] )
    
    # Only process nodes that are connected via links
    nodes = [node for node in all_nodes if node['id'] in connected_node_ids]
    
    excluded_count = len(all_nodes) - len(nodes)
    if excluded_count > 0:
        debug( f'✓ Filtering: {len( nodes )} connected workflow nodes, {excluded_count} unconnected elements ignored' )
    
    if not links or not nodes:
        print( 'No links or nodes to analyze.' )
        return {
            'status':   'success',
            'message':  'No links to analyze',
            'overlaps': []
        }
    
    # Build node map for quick lookup
    node_map = {node['id']: node for node in nodes}
    
    overlaps = []
    
    # Check each link
    for link in links:
        origin_id = link['origin_id']
        target_id = link['target_id']
        
        if origin_id not in node_map or target_id not in node_map:
            continue
        
        origin_node = node_map[origin_id]
        target_node = node_map[target_id]
        
        # Get link endpoints (treating as straight line for now)
        # Origin point: output port on origin node (right side)
        origin_x = origin_node['pos'][0] + origin_node['size'][0]
        origin_y = origin_node['pos'][1] + 30 + (link['origin_slot'] * 20)  # Approximate port position
        
        # Target point: input port on target node (left side)
        target_x = target_node['pos'][0]
        target_y = target_node['pos'][1] + 30 + (link['target_slot'] * 20)  # Approximate port position
        
        # Determine the horizontal range between origin and target
        min_x = min( origin_x, target_x )
        max_x = max( origin_x, target_x )
        
        # Check if this link intersects any node (except origin and target)
        # Only check nodes that are horizontally between the origin and target
        overlapping_nodes = []
        
        for node in nodes:
            node_id = node['id']
            
            # Skip the nodes this link connects to
            if node_id == origin_id or node_id == target_id:
                continue
            
            node_x     = node['pos'][0]
            node_w     = node['size'][0]
            node_right = node_x + node_w
            
            # Check if this node is horizontally between the origin and target
            # Node must overlap with the horizontal span of the link
            if node_right < min_x or node_x > max_x:
                # Node is completely outside the horizontal range
                continue
            
            node_y = node['pos'][1]
            node_h = node['size'][1]
            
            # Check if link intersects this node
            if line_segment_intersects_rect(
                origin_x, origin_y,
                target_x, target_y,
                node_x, node_y,
                node_w, node_h
            ):
                overlapping_nodes.append( {
                    'node_id':   node_id,
                    'node_type': node['type'],
                    'node_pos':  [node_x, node_y]
                } )
        
        if overlapping_nodes:
            overlap_info = {
                'link_id':           link['id'],
                'origin_id':         origin_id,
                'origin_type':       origin_node['type'],
                'target_id':         target_id,
                'target_type':       target_node['type'],
                'overlapping_nodes': overlapping_nodes
            }
            overlaps.append( overlap_info )
    
    debug( f'\n✓ Found {len( overlaps )} links with overlaps:' )
    
    # Track cumulative offsets for links going up or down
    up_offset   = 50  # First link up starts at 50
    down_offset = 50  # First link down starts at 50
    
    # Step 2: Determine reroute direction for each overlapping link
    for overlap in overlaps:
        origin_id = overlap['origin_id']
        target_id = overlap['target_id']
        
        origin_node = node_map[origin_id]
        target_node = node_map[target_id]
        
        # Get link endpoints
        origin_x = origin_node['pos'][0] + origin_node['size'][0]
        origin_y = origin_node['pos'][1] + 30 + (next( link['origin_slot'] for link in links if link['id'] == overlap['link_id'] ) * 20)
        
        target_x = target_node['pos'][0]
        target_y = target_node['pos'][1] + 30 + (next( link['target_slot'] for link in links if link['id'] == overlap['link_id'] ) * 20)
        
        # Determine the horizontal range between origin and target
        min_x = min( origin_x, target_x)
        max_x = max( origin_x, target_x )
        
        # Find highest and lowest nodes in ALL columns the link passes through
        # Not just the ones it directly overlaps
        highest_node_top   = None
        lowest_node_bottom = None
        highest_node_id    = None
        highest_node_type  = None
        lowest_node_id     = None
        lowest_node_type   = None
        
        # Check all nodes in the horizontal range between origin and target
        for node in nodes:
            node_id = node['id']
            
            # Skip the nodes this link connects to
            if node_id == origin_id or node_id == target_id:
                continue
            
            node_x     = node['pos'][0]
            node_w     = node['size'][0]
            node_right = node_x + node_w
            
            # Check if this node is horizontally between the origin and target
            if node_right < min_x or node_x > max_x:
                # Node is completely outside the horizontal range
                continue
            
            # This node is in a column that the link passes through
            node_top    = node['pos'][1]
            node_bottom = node['pos'][1] + node['size'][1]
            
            if highest_node_top is None or node_top < highest_node_top:
                highest_node_top  = node_top
                highest_node_id   = node_id
                highest_node_type = node['type']
            
            if lowest_node_bottom is None or node_bottom > lowest_node_bottom:
                lowest_node_bottom = node_bottom
                lowest_node_id     = node_id
                lowest_node_type   = node['type']
        
        # Calculate vertical distances for routing above or below
        # For routing UP: need to clear the highest node's top
        # Distance = how far up from the HIGHER of the two endpoints
        higher_y = max( origin_y, target_y )
        lower_y = min( origin_y, target_y )
        
        # Distance to route above highest node
        up_distance = higher_y - highest_node_top if highest_node_top < higher_y else 0
        
        # Distance to route below lowest node
        down_distance = lowest_node_bottom - lower_y if lowest_node_bottom > lower_y else 0
        
        # Determine which path requires less vertical movement
        if up_distance < down_distance:
            reroute_direction = 'up'
            # Place above the highest node using current up_offset
            reroute_y = highest_node_top - up_offset
            up_offset += 20  # Increase offset for next link going up

        else:
            reroute_direction = 'down'
            # Place below the lowest node using current down_offset
            reroute_y = lowest_node_bottom + down_offset
            down_offset += 20  # Increase offset for next link going down
        
        # Calculate horizontal positions for reroutes
        # First reroute: at the start of the first column after the starting node
        reroute1_x = origin_x + 50  # 50 units to the right of origin node
        
        # Second reroute: at the end of the column that precedes the ending node
        reroute2_x = target_x - 50  # 50 units to the left of target node
        
        # Create reroute positions
        reroute1_pos = [reroute1_x, reroute_y]
        reroute2_pos = [reroute2_x, reroute_y]
        
        # Store the decision
        overlap['reroute_direction'] = reroute_direction
        overlap['up_distance']       = up_distance
        overlap['down_distance']     = down_distance
        overlap['highest_node_top']  = highest_node_top
        overlap['highest_node_id']   = highest_node_id

        debug( f'    → Reroute 1 position: {reroute1_pos}' )
        debug( f'    → Reroute 2 position: {reroute2_pos}' )

        overlap['highest_node_type']  = highest_node_type
        overlap['lowest_node_bottom'] = lowest_node_bottom
        overlap['lowest_node_id']     = lowest_node_id
        overlap['lowest_node_type']   = lowest_node_type
        overlap['reroute1_pos']       = reroute1_pos
        overlap['reroute2_pos']       = reroute2_pos
        overlap['reroute_y']          = reroute_y
        
        # Print results
        debug( f'\n  Link {overlap["link_id"]}: {overlap["origin_type"]}({overlap["origin_id"]}) -> {overlap["target_type"]}({overlap["target_id"]})' )
        debug( f'    Overlaps {len(overlap["overlapping_nodes"])} node(s):' )

        for node_info in overlap['overlapping_nodes']:
            debug( f'      - {node_info["node_type"]}({node_info["node_id"]}) at {node_info["node_pos"]}' )

        debug( f'    Highest node: {highest_node_type}({highest_node_id}) top at Y={highest_node_top}' )
        debug( f'    Lowest node: {lowest_node_type}({lowest_node_id}) bottom at Y={lowest_node_bottom}' )
        debug( f'    Combined distance to top: {up_distance:.1f}' )
        debug( f'    Combined distance to bottom: {down_distance:.1f}' )
        debug( f'    → Reroute link {overlap["link_id"]} {reroute_direction.upper()}' )
    
    debug( '\n' + '-'*50 )
    debug( 'Reroute Summary:' )
    for overlap in overlaps:
        debug( f'  Reroute link {overlap["link_id"]} {overlap["reroute_direction"]}' )
    
    debug( '\n' + '='*50 )
    debug( '' )
    
    return {
        'status':   'success',
        'message':  f'Found {len(overlaps)} overlapping links',
        'overlaps': overlaps
    }