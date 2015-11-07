#include <curl/curl.h>
#include <iostream>
#include <thread>
#include <unistd.h>
#include "json.h"

#include "DogDatabase.hpp"
#include "CoordUploader.hpp"
#include "CConvertors.hpp"

using namespace std;

static const string coordUploadRequest = "/api/collar/add_point/";

namespace dognetd
{
	CoordUploader::CoordUploader( DogDatabase &db, ArduinoController &arduino, const string &url, const string &hash ):
		db( &db ),
		arduino( &arduino ),
		url( url ),
		hash( hash ),
		interrupted( false )
	{
		curl_global_init( CURL_GLOBAL_ALL );
		curl = curl_easy_init( );
	}
	
	CoordUploader::~CoordUploader( void )
	{
		stop( );
		curl_global_cleanup( );
	}
	
	void CoordUploader::start( void )
	{
		interrupted = false;
		uploader = thread( &CoordUploader::run, this );
	}
	
	void CoordUploader::stop( void )
	{
		interrupted = true;
		uploader.join( );
	}
	
	void CoordUploader::run( void )
	{
		cout << "uploader thread started\n";
		
		while ( !interrupted )
		{
			// get coordinates from db
			vector< Coordinate > coords = db->getCoordinates( 10 );
			
			// upload to server
			cout << "got " << CConvertors::int2str( coords.size() ) << " coordinates to upload\n";
			for ( vector< Coordinate >::iterator it = coords.begin( ); it != coords.end( ); ++it )
			{
				if ( uploadSingle( *it ) )
					db->removeCoordinate( it->id );
			}
			
			// perform check every second
			if ( coords.empty( ) )
				sleep( 1 );
		}
		
		cout << "uploader thread stopped\n";
	}
	
	static size_t writeFunc( void *ptr, size_t size, size_t nmemb, string *str )
	{
		str->append( ( char* )ptr, nmemb );
		return size * nmemb;
	}
	
	bool CoordUploader::uploadSingle( const Coordinate &coord )
	{
		if ( !curl )
			return false;
		
		string get = "?collar_id_hash=" + hash + "&timestamp=" + CConvertors::int2str( coord.timestamp ) +
			"&lat=" + coord.latitude + "&lon=" + coord.longitude;
		string full_url = url + coordUploadRequest + get;
		
		string response;
		
		curl_easy_setopt( curl, CURLOPT_URL, full_url.c_str( ) );
		curl_easy_setopt( curl, CURLOPT_WRITEFUNCTION, writeFunc );
		curl_easy_setopt( curl, CURLOPT_WRITEDATA, &response );

		CURLcode res = curl_easy_perform( curl );
		if ( res != CURLE_OK )
			cout << "curl_easy_perform failed: " << string( curl_easy_strerror( res ) ) << endl;
		else
			cout << "coordinate uploaded: (" << coord.latitude + ", " << coord.longitude << ")\n";
		
		processResponse( response );

		return res == CURLE_OK;
	}
	
	void CoordUploader::processResponse( const string &response )
	{
		
	}
}
