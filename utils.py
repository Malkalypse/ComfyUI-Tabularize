def set_debug( debug_level ):
    '''
    Prints if the debug level is equal or higher than a set value.
    
    Args:
        debug_level: The debug level threshold (0 = no debug output, higher = more verbose)
    
    Returns:
        A debug function that takes (message, lvl=1) and prints conditionally
    '''

    def debug( message, lvl=1 ):
        if debug_level >= lvl:
            print( message )
    
    return debug
