import { app } from '../../scripts/app.js';
import { api } from '../../scripts/api.js';
import { log as logger, setDebug, updateNodeID } from './utils.js';

const DEBUG = 0;
const PATH = '/tabularize/action';

const log = (msg) => logger( msg, PATH );
const debug = setDebug( log, DEBUG );

/** Create multiple reroutes for a link at specified positions
 * @param {number} linkId - The ID of the link to add reroutes to
 * @param {Array<[number, number]>} positions - Array of [x, y] coordinate pairs
 * @returns {Promise<Array>} Array of created reroute IDs
 */
async function createReroutesAtPositions( linkId, positions ) {
	const graph = app.graph;
	
	// Validate inputs
	if( !linkId || !positions || !Array.isArray( positions ) || positions.length === 0 ) {
		await log( 'Invalid parameters. Expected linkId and array of [x, y] positions.' );
		return [];
	}
	
	// Get the link
	const link = graph.links.get( linkId );
	if( !link ) {
		await log( `Link ${linkId} not found!` );
		return [];
	}
	
	// Get Reroute constructor from LiteGraph
	if( typeof LiteGraph === 'undefined' || !LiteGraph.Reroute ) {
		await log( 'ERROR: LiteGraph.Reroute is not available.' );
		return [];
	}
	const RerouteClass = LiteGraph.Reroute;
	
	const createdReroutes = [];
	
	try {
		// Create reroutes in order
		for( let i = 0; i < positions.length; i++ ) {
			const pos = positions[i];
			
			// Validate position
			if( !Array.isArray( pos ) || pos.length !== 2 || typeof pos[0] !== 'number' || typeof pos[1] !== 'number' ) {
				await log( `Warning: Skipping invalid position at index ${i}: ${JSON.stringify( pos )}` );
				continue;
			}
			
			const rerouteId = ++graph.state.lastRerouteId;
			
			// Parent is the previous reroute in the chain, or undefined for the first one
			const parentId = i > 0 ? createdReroutes[i - 1] : undefined;
			
			// Create the reroute
			const reroute = new RerouteClass(
				rerouteId,
				graph,
				[pos[0], pos[1]],
				parentId,
				[linkId]
			);
			
			// Add to graph
			graph.reroutes.set( rerouteId, reroute );
			createdReroutes.push( rerouteId );
			
			await debug( `  Created reroute ${rerouteId} at [${pos[0]}, ${pos[1]}] with parentId: ${parentId ?? 'none'}` );
		}
		
		// Update link to point to the last reroute in the chain
		if( createdReroutes.length > 0 ) {
			link.parentId = createdReroutes[createdReroutes.length - 1];
			await debug( `  Updated link ${linkId} to use reroute ${link.parentId}` );
		}
		
		// Force redraw
		if( graph.list_of_graphcanvas && graph.list_of_graphcanvas[0] ) {
			graph.list_of_graphcanvas[0].setDirty( true, true );
		}
		
		return createdReroutes;
		
	} catch( error ) {
		console.error( 'Error creating reroutes:', error );
		await log( `Error creating reroutes: ${error.message}` );
		return createdReroutes; // return any reroutes created before the error
	}
}


/** Helper function to collect graph data */
function collectGraphData() {
	const nodes = app.graph._nodes || [];
	const links = app.graph.links || {};
	
	// Convert nodes to simple data structure
	const nodeData = nodes.map( node => ( {
		id:	  node.id,
		type: node.type,
		pos:  [node.pos[0], node.pos[1]],
		size: [node.size[0], node.size[1]],

		inputs: node.inputs ? node.inputs.map( input => ( {
			name: input.name,
			type: input.type,
			link: input.link
		} ) ) : [],

		outputs: node.outputs ? node.outputs.map( output => ( {
			name:  output.name,
			type:  output.type,
			links: output.links || []
		} ) ) : []
	} ) );
	
	// Convert links to simple data structure
	const linkData = Object.values( links ).map( link => ( {
		id:          link.id,
		origin_id:   link.origin_id,
		origin_slot: link.origin_slot,
		target_id:   link.target_id,
		target_slot: link.target_slot,
		type:        link.type
	} ) );
	
	return {
		nodes: nodeData,
		links: linkData
	};
}


/** Reindex node IDs sequentially based on position (left to right, top to bottom within columns) */
async function reindexNodeIDs( positions ) {
	await debug( 'Reindexing node IDs...' );
	
	const graph = app.graph;
	
	// Get all nodes that were positioned
	const nodesToReindex = Object.keys( positions ).map( id => {
		const node = graph.getNodeById( parseInt( id ) );
		if( !node ) return null;
		return {
			node: node,
			x: positions[id][0],
			y: positions[id][1]
		};
	} ).filter( n => n !== null );
	
	if( nodesToReindex.length === 0 ) {
		await debug( 'No nodes to reindex' );
		return;
	}
	
	// Sort by x position (column), then by y position (row within column)
	nodesToReindex.sort( (a, b) => {
		if( Math.abs( a.x - b.x ) < 10 ) { // Same column (within 10px tolerance)
			return a.y - b.y; // Sort by y (top to bottom)
		}
		return a.x - b.x; // Sort by x (left to right)
	} );
	
	// Find highest existing node ID to avoid conflicts
	let maxId = 0;
	for( const nodeEntry of graph._nodes ) {
		if( nodeEntry && nodeEntry.id > maxId ) {
			maxId = nodeEntry.id;
		}
	}
	
	// First pass: reindex to temporary high IDs to avoid conflicts
	const tempStartId = maxId + 1;
	await debug( `First pass: reindexing ${nodesToReindex.length} nodes starting from ${tempStartId}...` );
	for( let i = 0; i < nodesToReindex.length; i++ ) {
		const tempId = tempStartId + i;
		updateNodeID( nodesToReindex[i].node, tempId );
	}
	
	// Second pass: reindex to final sequential IDs starting from 1
	await debug( `Second pass: reindexing to final IDs starting from 1...` );
	for( let i = 0; i < nodesToReindex.length; i++ ) {
		const finalId = i + 1;
		updateNodeID( nodesToReindex[i].node, finalId );
	}
	
	await debug( `✓ Reindexed ${nodesToReindex.length} nodes` );
	graph.setDirtyCanvas( true, true );
}


/** Reindex link IDs sequentially based on origin node order and output slot */
async function reindexLinkIDs() {
	await debug( 'Reindexing link IDs...' );
	
	const graph = app.graph;
	
	// Get all links
	const linksToReindex = [];
	for( const [linkId, link] of graph.links.entries() ) {
		if( link ) {
			linksToReindex.push( link );
		}
	}
	
	if( linksToReindex.length === 0 ) {
		await debug( 'No links to reindex' );
		return;
	}
	
	// Sort by origin node ID, then by origin slot, then by target node ID, then by target slot
	linksToReindex.sort( (a, b) => {
		if( a.origin_id !== b.origin_id ) {
			return a.origin_id - b.origin_id;
		}
		if( a.origin_slot !== b.origin_slot ) {
			return a.origin_slot - b.origin_slot;
		}
		if( a.target_id !== b.target_id ) {
			return a.target_id - b.target_id;
		}
		return a.target_slot - b.target_slot;
	} );
	
	// Find highest existing link ID to avoid conflicts
	let maxId = 0;
	for( const link of linksToReindex ) {
		if( link.id > maxId ) {
			maxId = link.id;
		}
	}
	
	// First pass: reindex to temporary high IDs to avoid conflicts
	const tempStartId = maxId + 1;
	await debug( `First pass: reindexing ${linksToReindex.length} links starting from ${tempStartId}...` );
	for( let i = 0; i < linksToReindex.length; i++ ) {
		const link = linksToReindex[i];
		const oldId = link.id;
		const tempId = tempStartId + i;
		
		// Update node references to this link ID
		const originNode = graph.getNodeById( link.origin_id );
		const targetNode = graph.getNodeById( link.target_id );
		
		if( originNode && originNode.outputs && originNode.outputs[link.origin_slot] ) {
			const output = originNode.outputs[link.origin_slot];
			if( output.links ) {
				const linkIndex = output.links.indexOf( oldId );
				if( linkIndex !== -1 ) {
					output.links[linkIndex] = tempId;
				}
			}
		}
		
		if( targetNode && targetNode.inputs && targetNode.inputs[link.target_slot] ) {
			const input = targetNode.inputs[link.target_slot];
			if( input.link === oldId ) {
				input.link = tempId;
			}
		}
		
		// Remove old entry and add new one
		graph.links.delete( oldId );
		link.id = tempId;
		graph.links.set( tempId, link );
	}
	
	// Second pass: reindex to final sequential IDs starting from 1
	await debug( `Second pass: reindexing to final IDs starting from 1...` );
	for( let i = 0; i < linksToReindex.length; i++ ) {
		const link = linksToReindex[i];
		const oldId = link.id;
		const finalId = i + 1;
		
		// Update node references to this link ID
		const originNode = graph.getNodeById( link.origin_id );
		const targetNode = graph.getNodeById( link.target_id );
		
		if( originNode && originNode.outputs && originNode.outputs[link.origin_slot] ) {
			const output = originNode.outputs[link.origin_slot];
			if( output.links ) {
				const linkIndex = output.links.indexOf( oldId );
				if( linkIndex !== -1 ) {
					output.links[linkIndex] = finalId;
				}
			}
		}
		
		if( targetNode && targetNode.inputs && targetNode.inputs[link.target_slot] ) {
			const input = targetNode.inputs[link.target_slot];
			if( input.link === oldId ) {
				input.link = finalId;
			}
		}
		
		// Remove old entry and add new one
		graph.links.delete( oldId );
		link.id = finalId;
		graph.links.set( finalId, link );
	}
	
	await debug( `✓ Reindexed ${linksToReindex.length} links` );
	graph.setDirtyCanvas( true, true );
}


/** Main organization function - sends data to Python */
async function organizeNodes() {
	try {
		await debug( 'Collecting graph data...' );
		const graphData = collectGraphData();
		
		await debug( 'Sending to Python for processing...' );

		const response = await api.fetchApi( '/tabularize/action', {
			method:  'POST',
			headers: { 'Content-Type': 'application/json' },
			body:    JSON.stringify( {action: 'organize', graph: graphData} )
		} );
		
		const result = await response.json();
		
		if( result.error ) {
			await log( `Error: ${result.error}` );
			return;
		}
		
		// Apply position changes (if any)
		const positions = result.positions || {};
		const sizes     = result.sizes || {};
		
		if( Object.keys( positions ).length > 0 ) {
			await debug( `Applying new positions and sizes for ${Object.keys( positions ).length} nodes...` );
				
			// Normal mode: apply all at once
			for( const [nodeId, pos] of Object.entries( positions ) ) {
				const node = app.graph.getNodeById( parseInt( nodeId ) );
				if( node ) {
					node.pos = pos;
					
					// Apply size if specified
					if( sizes[nodeId] ) {
						node.size = sizes[nodeId];
					}
				}
			}

			app.graph.setDirtyCanvas( true, true );

			await debug( '✓ Organization complete!' );
			
			// Automatically reroute links after organizing
			await rerouteLinks();
		
			// Reindex node IDs sequentially
			await reindexNodeIDs( positions );
			
			// Reindex link IDs sequentially
			await reindexLinkIDs();
		}
	} catch( e ) {
		await log( `Error: ${e.message}` );
		console.error( 'Tabularize error:', e );
	}
}


/** Remove all reroutes from the graph */
async function removeAllReroutes() {
	const graph = app.graph;
	if( !graph.reroutes || graph.reroutes.size === 0 ) return;
	
	const count = graph.reroutes.size;
	await debug( `Removing all ${count} reroutes...` );
	
	// Clear all link parentIds
	for( const [linkId, link] of graph.links.entries() ) {
		if( link && link.parentId ) {
			link.parentId = undefined;
		}
	}
	
	// Clear all reroutes
	graph.reroutes.clear();
	
	// Reset reroute ID counter
	graph.state.lastRerouteId = 0;
}


/** Reroute Links function - detects overlapping links */
async function rerouteLinks() {
	try {
		// Remove all existing reroutes first
		await removeAllReroutes();
		
		await debug( 'Collecting graph data for overlap detection...', 2 );
		const graphData = collectGraphData();
		
		await debug( 'Analyzing link overlaps...', 2 );
		const response = await api.fetchApi( '/tabularize/action', {
			method:  'POST',
			headers: { 'Content-Type': 'application/json' },
			body:    JSON.stringify( {action: 'reroute', graph: graphData} )
		} );
		
		const result = await response.json();
		
		if( result.error ) {
			await log( `Error: ${result.error}` );
			return;
		}
		
		const overlaps = result.overlaps || [];
		await debug( `✓ Analysis complete: Found ${overlaps.length} overlapping links`, 2 );
		
		if( overlaps.length > 0 ) {
			await debug( 'Adding reroute points to links...', 2 );
			
			// Process each overlapping link
			for( const overlap of overlaps ) {
				const linkId = overlap.link_id;
				
				await debug( `  Processing link ${linkId}...`, 2 );
				
				// Create reroutes at the positions provided by the backend
				const positions = [
					overlap.reroute1_pos,
					overlap.reroute2_pos
				];
				
				const createdReroutes = await createReroutesAtPositions( linkId, positions );
				
				if( createdReroutes.length > 0 ) {
					await debug( `  ✓ Created ${createdReroutes.length} reroutes for link ${linkId}`, 2 );
				} else {
					await log( `  ✗ Failed to create reroutes for link ${linkId}` );
				}
			}
			
			await debug( `✓ Added reroute points for ${overlaps.length} links`, 2 );
		}
		
		await debug( '✓ Reroute Links complete!', 2 );
		
	} catch( e ) {
		await log( `Error: ${e.message}` );
		console.error( 'Tabularize error:', e );
	}
}


// Extension registration
debug( 'Tabularize extension loaded' );

app.registerExtension( {
	name: 'Tabularize.ContextMenu',
	
	async setup() {
		debug( '✓ Tabularize setup complete' );
		
		// Override the canvas menu
		const getCanvasMenuOptions = LGraphCanvas.prototype.getCanvasMenuOptions;
		
		LGraphCanvas.prototype.getCanvasMenuOptions = function () {
			const options = getCanvasMenuOptions.apply( this, arguments );
			
			options.push( null ); // separator

			options.push( {
				content:  '🔲 Tabularize - Organize Columns',
				callback: () => organizeNodes()
			} );

			options.push( {
				content:  '🔗 Tabularize - Reroute Links',
				callback: () => rerouteLinks()
			} );		

			return options;
		};
	}
} );