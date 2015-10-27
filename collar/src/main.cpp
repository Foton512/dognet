#include <iostream>
#include <vector>
#include <string>

#include "CConvertors.hpp"
#include "CommandServer.hpp"
#include "DogDatabase.hpp"
#include "CoordUploader.hpp"
#include "CoordsReader.hpp"

#include "md5.hpp"

using namespace std;
using namespace dognetd;

const int serverPort = 8888;

int main( int argc, char **argv )
{
	if ( argc != 4 )
	{
		cout << "Usage: dognetd <server> <port> <collar_id>\n";
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
	string serverAddr = string( argv[1] ) + ":" + string( argv[2] );
	cout << "Server: " << serverAddr << endl;
	
	CommandServer server( serverPort );
	if ( server.start( ) )
		cout << "Command server started\n";
	else
	{
		cout << "Could not start command server\n";
		return 0;
	}
	
	DogDatabase database( "dog.db" );
	database.open( );
	database.createCoordinatesTable( );
	
	CoordsReader reader( database, "/dev/ttyUSB0" );
	reader.start();

	CoordUploader uploader( database, serverAddr, hash );
	uploader.start( );
	
	cin.get( );

	uploader.stop( );
	reader.stop();
	database.close( );
	server.stop( );

	return 0;
}
