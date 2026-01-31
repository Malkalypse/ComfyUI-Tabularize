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