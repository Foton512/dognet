#include <thread>
#include <iostream>
#include <string>
#include <sstream>

#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>

#include "DogDatabase.hpp"
#include "CConvertors.hpp"
#include "ArduinoController.hpp"

using namespace std;

static const int bufferSize = 1024;

namespace dognetd
{
	ArduinoController::ArduinoController( DogDatabase &db, const string &device ):
		db( &db ),
		device( device ),
		device_fd( -1 )
	{ }
	
	ArduinoController::~ArduinoController( void )
	{
		stop( );
	}
	
	bool ArduinoController::start( void )
	{
		device_fd = open( device.c_str( ), O_RDWR );
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
		reader = thread( &ArduinoController::run, this );
		sleep( 3 );
		return true;
	}
	
	void ArduinoController::stop( void )
	{
		interrupted = true;
		reader.join( );
		close( device_fd );
		device_fd = -1;
	}
	
	bool ArduinoController::configureDevice( void )
	{
		fcntl( device_fd, F_SETFL, 0 );
			
		// get the current options
		struct termios options;
		tcgetattr( device_fd, &options );

		// set options
		options.c_cflag = ( CLOCAL | CREAD );

		// 8n1
		options.c_cflag &= ~PARENB;
		options.c_cflag &= ~CSTOPB;
		options.c_cflag &= ~CSIZE;
		options.c_cflag |= CS8;
		options.c_iflag = ( IGNPAR | IGNBRK );
		options.c_lflag       = 0;
		options.c_oflag       = 0;
		options.c_cc[ VMIN ]  = 0;
		options.c_cc[ VTIME ] = 20;
		cfsetispeed( &options, B9600 );
		cfsetospeed( &options, B9600 );

		// write options
		tcflush( device_fd, TCIFLUSH );
		tcsetattr( device_fd, TCSANOW, &options );

		return true;
	}
	
	void ArduinoController::run( void )
	{
		cout << "arduino thread started\n";
		
		fd_set readset;
		FD_ZERO( &readset );
		FD_SET( device_fd, &readset );
		
		struct timeval tv;
		tv.tv_sec = 1;
		tv.tv_usec = 0;
		
		char buffer[ bufferSize + 1 ];
		int count = 0;
		int result = 0;
		while ( !interrupted )
		{
			result = select( device_fd + 1, &readset, NULL, NULL, &tv );
			if ( result && FD_ISSET( device_fd, &readset ) )
			{
				count = read( device_fd, buffer, bufferSize );
				if ( count > 0 )
				{
					//TODO
					cout << "got from arduino: " << string( buffer, count ) << endl;
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
		cout << "arduino thread stopped\n";
	}
	
	bool ArduinoController::send( std::string line )
	{
		if ( device_fd == -1 )
			return 0;

		// write length (2 bytes, ASCII)
		string len = CConvertors::int2str( line.size( ) );
		CConvertors::frontResizeString( &len, 2, '0' );
		int result = write( device_fd, len.c_str( ), 2 );
		if ( result == 0 )
		{
			cout << "write failed, device closed\n";
			return false;
		}
		if ( result == -1 )
		{
			cout << "write failed, error code: " << CConvertors::int2str( errno ) << endl;
			return false;
		}
		
		// write data
		result = write( device_fd, line.c_str( ), line.size( ) );
		if ( result == 0 )
		{
			cout << "write failed, device closed\n";
			return false;
		}
		if ( result == -1 )
		{
			cout << "write failed, error code: " << CConvertors::int2str( errno ) << endl;
			return false;
		}
		
		cout << "written to arduino (" << CConvertors::int2str( result ) << "): " << line << endl;
		return true;
	}
	
	bool ArduinoController::lcdLine( int line, string text )
	{
		string toSend;
		
		// add display text command id
		toSend += "1,";
		
		// add line number
		toSend += CConvertors::int2str( line ) + ",";
		
		// add text
		toSend += text;
		
		return send( toSend );
	}
	
	bool ArduinoController::lcdClear( void )
	{
		string toSend;
		
		// add display clear command id
		toSend += "2";
		
		return send( toSend );
	}
	
	bool ArduinoController::lcdBacklight(void )
	{
		string toSend;
		
		// add backlight command
		toSend += "3";
		
		return send( toSend );
	}
	
	bool ArduinoController::ledBlink( ArduinoController::LedType led )
	{
		string toSend;
		
		// add led blink command
		toSend += "4,";
		
		// add led type
		toSend += ( char )led;
		
		return send( toSend );
	}
	
}
