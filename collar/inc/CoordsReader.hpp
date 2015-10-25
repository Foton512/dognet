/* 
 * File:   CoordsReader.hpp
 * Author: asu
 *
 * Created on October 25, 2015, 12:43 PM
 */

#ifndef COORDSREADER_HPP
#define	COORDSREADER_HPP

#include <thread>
#include <string>

#include "DogDatabase.hpp"

namespace dognetd
{
	// reads coordinates from GPS stores to database
	class CoordsReader
	{
		public:
			CoordsReader( DogDatabase &db, const std::string &device );
			~CoordsReader( void );
			bool start( void );
			void stop( void );
			
		private:
			DogDatabase *db;
			std::string device;
			
			std::thread uploader;
			bool interrupted;
			int device_fd;
			
			void run( void );
			bool configureDevice( void );
			void processData( const std::string &data );
	};
}

#endif	/* COORDSREADER_HPP */

