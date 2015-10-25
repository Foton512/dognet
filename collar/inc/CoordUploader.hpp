/* 
 * File:   CoordUploader.hpp
 * Author: asu
 *
 * Created on October 24, 2015, 8:47 PM
 */

#ifndef COORDUPLOADER_HPP
#define	COORDUPLOADER_HPP

#include <thread>
#include <curl/curl.h>
#include "DogDatabase.hpp"

namespace dognetd
{
	// uploading coordinates to server
	class CoordUploader
	{
		public:
			CoordUploader( DogDatabase &db, const string &url, const string &hash );
			~CoordUploader( void );
			
			void start( void );
			void stop( void );
			
		private:
			DogDatabase *db;
			CURL *curl;
			string url;
			string hash;
			
			std::thread uploader;
			bool interrupted;
			
			void run( void );
			bool uploadSingle( const Coordinate &coord );
	};
}

#endif	/* COORDUPLOADER_HPP */

