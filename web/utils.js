import { api } from '../../scripts/api.js';

// Helper function to log to Python console
export async function log( message, path ) {
	try {
		await api.fetchApi( path, {
			method:  'POST',
			headers: {'Content-Type': 'application/json'},
			body:    JSON.stringify( {action: 'log', message} )
		} );
	} catch( e ) {
		console.error( 'Failed to send log to Python backend:', e );
	}
}

export function setDebug( logFn, debugLevel ) {
  return function debug( message, lvl = 1 ) {
    if( debugLevel >= lvl ) {
      return logFn( message );
    }
  };
}


// Update node ID and all associated links
export function updateNodeID( nodeRef, newId ) {

  const oldId = nodeRef.id;

	// Update all links that reference this node
	if( nodeRef.graph.links ) {
		for( const linkId in nodeRef.graph.links ) {
			const link = nodeRef.graph.links[ linkId ];
			if( link ) {
				if( link.origin_id === oldId ) {
					link.origin_id = newId;
				}
				if( link.target_id === oldId ) {
					link.target_id = newId;
				}
			}
		}
	}
	
	// Update the node ID in the graph registry
	delete nodeRef.graph._nodes_by_id[ oldId ];
	nodeRef.id = newId;
	nodeRef.graph._nodes_by_id[ newId ] = nodeRef;
}
