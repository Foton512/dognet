#include <iostream>
#include <vector>

#include "CConvertors.hpp"
#include "CommandServer.hpp"
#include "DogDatabase.hpp"

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
	database.addCoordinate( "test coords0" );
	database.addCoordinate( "test coords1" );
	database.addCoordinate( "test coords2" );
	
	vector<Coordinate> coords = database.getCoordinates( 10 );
	size_t size = coords.size( );
	for ( size_t i = 0; i < size; ++i )
		cout << CConvertors::int2str( coords[i].id ) << ") time = " << CConvertors::int2str( coords[i].timestamp ) << " coord = " << coords[i].coord << "\n";
		
	database.removeCoordinate( coords[0].id );
	
	coords = database.getCoordinates( 10 );
	size = coords.size( );
	for ( size_t i = 0; i < size; ++i )
		cout << CConvertors::int2str( coords[i].id ) << ") time = " << CConvertors::int2str( coords[i].timestamp ) << " coord = " << coords[i].coord << "\n";
	
	database.close( );
	
	cin.get( );

	server.stop( );
	cout << "Command server stopped\n";
	return 0;
}
