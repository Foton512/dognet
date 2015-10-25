#include <iostream>
#include <vector>

#include "CConvertors.hpp"
#include "CommandServer.hpp"
#include "DogDatabase.hpp"
#include "CoordUploader.hpp"
#include "CoordsReader.hpp"

using namespace std;
using namespace dognetd;

const int serverPort = 8888;

int main( )
{
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

	CoordUploader uploader( database, "http://188.166.64.150:8000", "c4ca4238a0b923820dcc509a6f75849b" );
	uploader.start( );
	
	cin.get( );

	uploader.stop( );
	reader.stop();
	database.close( );
	server.stop( );

	return 0;
}
