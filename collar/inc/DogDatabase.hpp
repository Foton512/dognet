#ifndef DOGDATABASE_H_
#define DOGDATABASE_H_

#include <ctime>
#include <sqlite3.h>
#include <string>
#include <vector>
#include <map>

using namespace std;

namespace dognetd
{
	// structure for coordinates uploading
	struct Coordinate
	{
		int id;
		time_t timestamp;
		string latitude;
		string longitude;
		
		Coordinate( int id, time_t timestamp, const string &latitude, const string &longitude ):
			id( id ),
			timestamp( timestamp ),
			latitude( latitude ),
			longitude( longitude )
		{ };
	};
	
	// class to manage sqlite database which stores dog data
	class DogDatabase
	{
		public:
			DogDatabase( const string &db_name );
			~DogDatabase( void );
			bool open( void );
			bool close( void );
			bool createCoordinatesTable( void );
			bool addCoordinate( const string &latitude, const string &longitude );
			vector<Coordinate> getCoordinates( int count );
			bool removeCoordinate( int id );

		private:
			sqlite3 *db;
			std::string db_name;
			
			bool sqlExecuteQuery( int ( *callback )( void*, int, char**, char** ), const string &query, void *output );
			bool sqlCreateTable( const std::string &table_name, const vector<string> &field_names,
				const vector<string> &field_types, const vector<string> &field_flags );
			bool sqlInsert( const string &table_name, const map<string,string> &fields );
			vector< map<string, string> > sqlSelect( const string &table_name, const vector<string> &fields,
					const string &condition, const string &additional );
			bool sqlRemove( const string &table_name, const string &field, const vector<string> &values );
	};
};

#endif // DOGDATABASE_H_
