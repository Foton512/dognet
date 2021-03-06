#include <iostream>
#include <vector>
#include <string>

#include <string.h>
#include <fcntl.h>
#include <sys/ioctl.h> 
#include <net/if.h>
#include <errno.h>
#include <unistd.h>

#include "CConvertors.hpp"
//#include "CommandServer.hpp"
#include "DogDatabase.hpp"
#include "CoordUploader.hpp"
#include "CoordsReader.hpp"
#include "ArduinoController.hpp"

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

// Get current date/time, format is YYYY-MM-DD-HH:mm:ss
static const string currentDateTime( void )
{
    time_t     now = time( 0 );
    struct tm  tstruct;
    char       buf[80];
    tstruct = *localtime( &now );
    
    // Visit http://en.cppreference.com/w/cpp/chrono/c/strftime
    // for more information about date/time format
    strftime( buf, sizeof( buf ), "%Y-%m-%d-%X", &tstruct );

    return buf;
}

int main( int argc, char **argv )
{
	if ( argc != 3 )
	{
		cout << "Usage: dognetd <external_server> <collar_id>\n";
		return 0;
	}
	
	// prepare log filenames
	string logApp = "/home/pi/app_" + currentDateTime( ) + ".txt";
	string logCoord = "/home/pi/app_" + currentDateTime( ) + ".txt";
	
//	// redirect cout to file
//	ofstream out( logApp );
//    cout.rdbuf( out.rdbuf( ) );
	
	// calculate md5 of collar id
	string id( argv[2] );
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
	
	DogDatabase database( "/home/pi/dog.db" );
	database.open( );
	database.createCoordinatesTable( );
	database.startFileLogging( logCoord );
	
	ArduinoController arduino( database, "/dev/ttyACM0" );
	arduino.start( );
	
	arduino.lcdClear( );
	arduino.lcdLine( 0, "Waiting for 3G..." );
	
	//TODO uncomment!
//	cout << "Waiting for ppp0 interface (3g)...\n";
//	while ( !is_interface_online( "ppp0" ) )
//		sleep( 2 );
	
//	int serverPort = CConvertors::str2int( string( argv[2] ) );
//	CommandServer server( serverPort );
//	if ( server.start( ) )
//		cout << "Command server started on port " << string( argv[2] ) << endl;
//	else
//	{
//		cout << "Could not start command server on port " << string( argv[2] ) << endl;
//		return 0;
//	}
	
	// we use "gps" symlink created by script in /etc/udev/rules.d
	CoordsReader reader( database, "/dev/gps" );
	reader.start( );

	CoordUploader uploader( database, arduino, serverAddr, hash );
	uploader.start( );
	
	database.addCoordinate( "3.1415926", "3.1415926" );
	
	// loop until signal
	while ( true )
		usleep( 1000 );

	return 0;
}
