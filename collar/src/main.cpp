#include <iostream>
#include <vector>
#include <string>

#include <string.h>
#include <fcntl.h>
#include <sys/ioctl.h> 
#include <net/if.h>
#include <errno.h>

#include "CConvertors.hpp"
#include "CommandServer.hpp"
#include "DogDatabase.hpp"
#include "CoordUploader.hpp"
#include "CoordsReader.hpp"

#include "md5.hpp"

using namespace std;
using namespace dognetd;

static bool is_interface_online( string interface )
{
    struct ifreq ifr;
    int sock = socket( AF_INET, SOCK_DGRAM, 0 );
    memset( &ifr, 0, sizeof( ifr ) );
    strcpy( ifr.ifr_name, interface.c_str( ) );
    if ( ioctl( sock, SIOCGIFFLAGS, &ifr ) < 0 )
    {
		cout << "Could not get " << interface << " status: "
			<< CConvertors::int2str( errno ) << endl;
		close( sock );
		return 0;
    }

    close( sock );
    
    int result = ifr.ifr_flags & IFF_UP;
    cout << "Status of " << interface << ": " << ( result ? "ON" : "OFF" ) << endl;
    return result;
}

int main( int argc, char **argv )
{
	if ( argc != 4 )
	{
		cout << "Usage: dognetd <external_server> <internal_server_port> <collar_id>\n";
		return 0;
	}
	
	// calculate md5 of collar id
	string id( argv[3] );
	MD5_CTX md5_ctx;
	MD5_Init( &md5_ctx );
	MD5_Update( &md5_ctx, id.c_str( ), id.size( ) );
	uint8_t md5[16];
	MD5_Final( md5, &md5_ctx );
	string hash = CConvertors::bin2hex( string( ( char * )md5, 16 ) );
	cout << "Collar hash: " << hash << endl;
	
	// capture server and port
	// http://188.166.64.150:8000
	string serverAddr = string( argv[1] );
	cout << "Server: " << serverAddr << endl;
	
	DogDatabase database( "dog.db" );
	database.open( );
	database.createCoordinatesTable( );
	
	cout << "Waiting for ppp0 interface (3g)...\n";
	while ( !is_interface_online( "ppp0" ) )
		sleep( 2 );
	
	int serverPort = CConvertors::str2int( string( argv[2] ) );
	CommandServer server( serverPort );
	if ( server.start( ) )
		cout << "Command server started on port " << string( argv[2] ) << endl;
	else
	{
		cout << "Could not start command server on port " << string( argv[2] ) << endl;
		return 0;
	}
	
	//TODO find gps device, do not use hardcode!
	CoordsReader reader( database, "/dev/ttyUSB0" );
	reader.start( );

	CoordUploader uploader( database, serverAddr, hash );
	uploader.start( );
	
	// loop until signal
	while ( true )
		usleep( 1000 );

	return 0;
}
