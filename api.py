'''
API route handlers for ComfyUI-Tabularize
Defines HTTP endpoints for JavaScript-Python communication
'''

from aiohttp import web  # type: ignore[import-not-found]
import server  # type: ignore[import-not-found]
from .tabularize import organize_nodes, detect_link_overlaps


# Action dispatch table with metadata
ACTION_HANDLERS = {
    'log': {
        'function': None,
        'data_key': 'message',
        'message': lambda d: f'[Tabularize] {d.get( "message", "" )}',
    },
    'organize': {
        'function': organize_nodes,
        'data_key': 'graph',
        'message': lambda d: '[Tabularize] Organizing nodes...',
    },
    'reroute': {
        'function': detect_link_overlaps,
        'data_key': 'graph',
        'message': lambda d: '[Tabularize] Detecting link overlaps...',
    },
}

# Tabularize API endpoint
@server.PromptServer.instance.routes.post( '/tabularize/action' )
async def tabularize_handler( request ):
    '''
    Unified endpoint for all Tabularize actions.
    
    Expected request body:
    {
        'action': 'log' | 'organize' | 'reroute',
        'message': '...' (for log action),
        'graph': {...} (for organize/reroute actions)
    }
    '''

    try:
        data = await request.json()
        action = data.get( 'action' )
        
        if action not in ACTION_HANDLERS:
            return web.json_response(
                {'error': f'Unknown action: {action}'},
                status=400
            )
        
        handler = ACTION_HANDLERS[action]
        
        # Print message
        print( handler['message']( data ) )
        
        # Execute function if specified
        if handler['function']:
            result = handler['function']( data.get( handler['data_key'], {} ) )
            return web.json_response( result )
        
        return web.json_response( {'status': 'success'} )
    
    except Exception as e:
        print( f'[Tabularize] Error: {e}' )
        import traceback
        traceback.print_exc()
        return web.json_response( {'error': str(e)}, status=500 )