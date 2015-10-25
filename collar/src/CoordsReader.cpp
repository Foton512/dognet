#include <thread>
#include <iostream>
#include <string>
#include <sstream>

#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>

#include "DogDatabase.hpp"
#include "CConvertors.hpp"
#include "CoordsReader.hpp"

using namespace std;

static const int bufferSize = 1024;

namespace dognetd
{
	CoordsReader::CoordsReader( DogDatabase &db, const string &device ):
		db( &db ),
		device( device ),
		device_fd( -1 )
	{ };
	
	CoordsReader::~CoordsReader( void )
	{
		stop( );
	}
	
	bool CoordsReader::start( void )
	{
		device_fd = open( device.c_str( ), O_RDWR | O_NOCTTY | O_NDELAY );
		if ( device_fd == -1 )
		{
			cout << "could not open " << device << ": " <<
					CConvertors::int2str( errno ) << endl;
			return false;
		}
		
		cout << device << " opened!\n";
		
		if ( !configureDevice( ) )
		{
			cout << "could not configure " << device << ": " <<
					CConvertors::int2str( errno ) << endl;
			close( device_fd );
			return false;
		}
		
		cout << device << " configured!\n";
		
		interrupted = false;
		uploader = thread( &CoordsReader::run, this );
		return true;
	}
	
	void CoordsReader::stop( void )
	{
		interrupted = true;
		uploader.join( );
		close( device_fd );
	}
	
	void CoordsReader::run( void )
	{
		cout << "reader thread started\n";
		
		fd_set readset;
		FD_ZERO( &readset );
		FD_SET( device_fd, &readset );
		
		struct timeval tv;
		tv.tv_sec = 1;
		tv.tv_usec = 0;
		
		char buffer[ bufferSize + 1 ];
		string data;
		int count = 0;
		int result = 0;
		while ( !interrupted )
		{
			//TODO remove govnocode
			result = select( device_fd + 1, &readset, NULL, NULL, &tv );
			if ( result && FD_ISSET( device_fd, &readset ) )
			{
				count = read( device_fd, buffer, bufferSize );
				if ( count > 0 )
				{
					buffer[ count ] = '\0';
					data = string( buffer );
					cout << "read " << CConvertors::int2str( count ) << " chars from " << device << ": " << data << endl;
					processData( data );
					sleep( 1 );
				}
				else if ( count == -1 )
				{
					cout << "could not read from " << device << ": " <<
						CConvertors::int2str( errno ) << endl;
					break;
				}
			}
			else if ( result == -1 )
			{
				cout << "select failed!\n";
				break;
			}
		}
		
		interrupted = false;
		cout << "reader thread stopped\n";
	}
	
	bool CoordsReader::configureDevice( void )
	{
		struct termios tty;
		struct termios tty_old;
		memset ( &tty, 0, sizeof tty );

		if ( tcgetattr ( device_fd, &tty ) != 0 )
		{
			std::cout << "Error " << errno << " from tcgetattr: " << strerror( errno ) << endl;
			return false;
		}

		// save old tty parameters
		tty_old = tty;

		// set Baud Rate
		cfsetospeed (&tty, (speed_t)B4800);
		cfsetispeed (&tty, (speed_t)B4800);

		// setting other Port Stuff
		tty.c_cflag     &=  ~PARENB;            // Make 8n1
		tty.c_cflag     &=  ~CSTOPB;
		tty.c_cflag     &=  ~CSIZE;
		tty.c_cflag     |=  CS8;

		tty.c_cflag     &=  ~CRTSCTS;           // no flow control
		tty.c_cc[VMIN]   =  1;                  // read doesn't block
		tty.c_cc[VTIME]  =  40;                  // 0.5 seconds read timeout
		tty.c_cflag     |=  CREAD | CLOCAL;     // turn on READ & ignore ctrl lines

		// make raw
		cfmakeraw( &tty );

		// flush Port, then apply attributes
		tcflush( device_fd, TCIFLUSH );
		if ( tcsetattr ( device_fd, TCSANOW, &tty ) != 0)
		{
			std::cout << "Error " << errno << " from tcsetattr" << endl;
			return false;
		}

		return true;
	}
	
	void CoordsReader::processData( const string &data )
	{
		// istringstream iss( data );
		string line;
		size_t found = data.find( "$GPRMC", 0 );
		if ( found != string::npos )
		{
			size_t end = data.find( "*", found );
			if ( end == string::npos )
				return;
			
			line = data.substr( found, end - found );
			cout << "processing line: " << line << endl;

			// line contains coordinates data
			vector<string> tokens = CConvertors::split( line, ',' );

			// check line structure
			if ( tokens.size( ) != 13 )
			{
				cout << "got broken RMC line\n";
				return;
			}

			// check whether data is accurate
			if ( tokens[2].at( 0 ) != 'A' )
			{
				cout << "data is not accurate\n";
				return;
			}

			// get latitude
			int latD = CConvertors::str2int( tokens[3].substr( 0, 2 ) ); // degrees
			double latM = CConvertors::str2double( tokens[3].substr( 2 ) ); // minutes

			// get latitude sign
			bool latPositive = ( tokens[4].at( 0 ) == 'N' );

			// get longitude
			int lonD = CConvertors::str2int( tokens[5].substr( 0, 3 ) ); // degrees
			double lonM = CConvertors::str2double( tokens[5].substr( 3 ) ); // minutes

			// get longitude sign
			bool lonPositive = ( tokens[6].at( 0 ) == 'E' );

			// calculate coordinates
			double latitude = ( double )latD + latM / 60.0;
			double longitude = ( double )lonD + lonM / 60.0;
			if ( !latPositive )
				latitude *= -1.0;
			if ( !lonPositive )
				longitude *= -1.0;

			// convert to string
			string strLat = to_string( latitude );
			string strLon = to_string( longitude );

			// store in db
			db->addCoordinate( strLat, strLon );
		}
	}


}

