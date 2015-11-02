/* 
 * File:   ArduinoController.hpp
 * Author: asu
 *
 * Created on November 1, 2015, 8:26 PM
 */

#ifndef ARDUINOCONTROLLER_HPP
#define	ARDUINOCONTROLLER_HPP

#include <thread>
#include <string>

#include "DogDatabase.hpp"

namespace dognetd
{
	class ArduinoController
	{
		enum LedType
		{
			LED_GREEN = 'g',
			LED_RED = 'r',
		};
		
		public:
			ArduinoController( DogDatabase &db, const std::string &device );
			~ArduinoController( void );
			bool start( void );
			void stop( void );
			
			bool lcdLine( int line, std::string text );
			bool lcdClear( void );
			bool lcdBacklight(void );
			bool ledBlink( LedType led );
			
		private:
			DogDatabase *db;
			std::string device;
			
			std::thread reader;
			bool interrupted;
			int device_fd;
			
			void run( void );
			bool configureDevice( void );
			bool send( std::string line );
	};
}

#endif	/* ARDUINOCONTROLLER_HPP */

