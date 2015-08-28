# -*- coding: UTF-8 -*-


from mcm.librouteros.datastructures import mksnt, parsresp, trapCheck, raiseIfFatal
from mcm.librouteros.exc import LibError


class Api:


    def __init__( self, rwo ):
        self.rwo = rwo


    def run( self, cmd, args = dict() ):
        '''
        Run any 'non interactive' command. Returns parsed response.

        cmd Command word eg. /ip/address/print.
        args Dictionary with key, value pairs.
        '''

        snt = (cmd,) + mksnt( args )
        self.rwo.writeSnt( snt )
        response = self._readResponse()
        trapCheck( response )
        raiseIfFatal( response )

        return parsresp( response )


    def _readResponse( self ):
        '''
        Read whole response.

        returns Read sentences as tuple.
        '''

        snts = []

        while True:

            snt = self.rwo.readSnt()
            snts.append( snt )

            if '!done' in snt:
                break

        return tuple( snts )


    def close( self ):
        '''
        Send /quit and close the connection.
        '''

        try:
            self.rwo.writeSnt( ('/quit',) )
            self.rwo.readSnt()
        except LibError:
            pass
        finally:
            self.rwo.close()


    def __del__( self ):
        '''
        On garbage collection run close().
        '''
        self.close()
