#include <string>
#include <vector>
#include <map>
#include <ctime>
#include <iostream>
#include <fstream>
#include <sqlite3.h>

#include "CConvertors.hpp"
#include "DogDatabase.hpp"

using namespace std;

const string coordTableName = "coordinates";
const string logFile = "log.txt";

namespace dognetd
{
	DogDatabase::DogDatabase( const string &db_name ):
		db_name( db_name ),
		db( NULL ),
		file( ),
		logToFile( false )
	{ }
	
	DogDatabase::~DogDatabase( void )
	{
		this->close( );
	}
	
	bool DogDatabase::open( void )
	{
		if ( db != NULL )
			return true; // already opened
		
		int rc = sqlite3_open( db_name.c_str( ), &db );
		if ( rc != SQLITE_OK )
		{
			cout << "Could not open database " << db_name << ": " << CConvertors::int2str( rc ) << endl;
			db = NULL;
			return false;
		}
		
		cout << "Database " << db_name << " opened successfully\n";
		return true;
	}
	
	bool DogDatabase::close( void )
	{
		int rc = sqlite3_close( db );
		if ( rc != SQLITE_OK )
		{
			cout << "Could not close database " << db_name << ": " << CConvertors::int2str( rc ) << endl;
			db = NULL;
			return false;
		}
		
		cout << "Database " << db_name << " closed successfully\n";
		db = NULL;
		return true;
	}
	
	bool DogDatabase::createCoordinatesTable( void )
	{
		vector<string> names;
		vector<string> types;
		vector<string> flags;
		
		// index field
		names.push_back( "id" );
		types.push_back( "INTEGER" );
		flags.push_back( "PRIMARY KEY AUTOINCREMENT NOT NULL" );
		
		// capture time (timestamp)
		names.push_back( "time" );
		types.push_back( "INTEGER" );
		flags.push_back( "" );
		
		// latitude
		names.push_back( "latitude" );
		types.push_back( "TEXT" );
		flags.push_back( "" );
		
		// longitude
		names.push_back( "longitude" );
		types.push_back( "TEXT" );
		flags.push_back( "" );
		
		// create table
		return sqlCreateTable( coordTableName, names, types, flags );
	}
	
	bool DogDatabase::addCoordinate( const string &latitude, const string &longitude )
	{
		map<string,string> fields;
		
		// add coordinates
		fields[ "latitude" ] = latitude;
		fields[ "longitude" ] = longitude;
		
		// add time
		time_t timestamp = time( NULL );
		string str_time = CConvertors::int2str( timestamp );
		fields[ "time" ] = str_time;
		
		// write to file if needed
		if ( logToFile )
			file << latitude << ", " << longitude << ", " << str_time << endl;
		
		// insert into coordinates table
		return sqlInsert( coordTableName, fields );
	}
	
	vector<Coordinate> DogDatabase::getCoordinates( int count )
	{
		// check input
		if ( count <= 0 )
			return vector<Coordinate>( );
		
		// get id, coordinate and time
		vector<string> fields;
		fields.push_back( "id" );
		fields.push_back( "time" );
		fields.push_back( "latitude" );
		fields.push_back( "longitude" );
		
		// prepare additional condition
		string addCondition( "ORDER BY time LIMIT " );
		addCondition += CConvertors::int2str( count );
		
		// execute
		vector< map<string, string> > result = sqlSelect( coordTableName, fields, "", addCondition );
		
		// convert to Coordinate
		vector<Coordinate> coords;
		for ( vector< map<string, string> >::iterator it = result.begin( ); it != result.end( ); ++it )
			coords.push_back( Coordinate( CConvertors::str2int( ( *it )[ "id" ] ),
				CConvertors::str2int( ( *it )[ "time" ] ), ( *it )[ "latitude" ], ( *it )[ "longitude" ] ) );
			
		return coords;
	}
	
	bool DogDatabase::removeCoordinate( int id )
	{
		vector<string> values;
		values.push_back( CConvertors::int2str( id ) );
		return sqlRemove( coordTableName, "id", values );
	}
	
	void DogDatabase::startFileLogging( void )
	{
		if ( !file.is_open( ) )
		{
			file.open( logFile );
			logToFile = true;
		}
	}
	
	void DogDatabase::endFileLogging( void )
	{
		if ( file.is_open( ) )
		{
			logToFile = false;
			file.close( );
		}
	}
	
	bool DogDatabase::sqlRemove( const string &table_name, const string &field, const vector<string> &values )
	{
		// validate table name
		if ( table_name.empty( ) )
			return false;
		
		// prepare request
		string request = "DELETE FROM " + table_name + " WHERE " + field;
		size_t count = values.size( );
		if ( count == 1 )
			request += " = " + values[0];
		else
		{
			string vals( " IN (" );
			for ( size_t i = 0; i < count; ++i )
			{
				vals += values[i];
				if ( i != count - 1 )
					vals += ", ";
			}
			vals += ")";
			request += vals;
		}
		
		// execute it
		return sqlExecuteQuery( NULL, request, NULL );
	};
	
	static int selectCallback( void *output, int columnsNum, char **values, char **columns )
	{
		vector< map<string, string> > *result = reinterpret_cast< vector<map<string, string> > * >( output );

		map<string, string> record;
		for ( size_t i = 0; i < columnsNum; ++i )
			record[ string( columns[i] ) ] = string( values[i] );
		
		result->push_back( record );
		return 0;
	}
	
	vector< map<string, string> > DogDatabase::sqlSelect( const string &table_name, const vector<string> &fields,
		const string &condition, const string &additional )
	{
		// validate table name
		if ( table_name.empty( ) )
			return vector< map<string, string> >( );
			
		// validate list
		if ( fields.empty( ) )
			return vector< map<string, string> >( );
		
		// prepare request
		string concat_fields;
		size_t size = fields.size( );
		for ( size_t i = 0; i < size; ++i )
		{
			concat_fields += fields[i];
			if ( i != size - 1 )
				concat_fields += ", ";
		}
		
		string request = "SELECT " + concat_fields + " FROM " + table_name;
		if ( !condition.empty( ) )
			request += " WHERE " + condition;
			
		request += " " + additional + ";";
		
		// prepare storage for result
		vector< map<string, string> > result;

		sqlExecuteQuery( selectCallback, request, reinterpret_cast<void *>( &result ) );
		return result;
	}
	
	bool DogDatabase::sqlInsert( const string &table_name, const map<string,string> &fields )
	{
		// validate list
		if ( fields.empty( ) )
			return false;
			
		// validate table name
		if ( table_name.empty( ) )
			return false;
			
		// create SQL request
		string names, values;
		for ( map<string,string>::const_iterator it = fields.begin( ); it != fields.end( ); ++it )
		{
			if ( !names.empty( ) )
			{
				names += ", ";
				values += ", ";
			}

			names += it->first;
			values += "'" + it->second + "'";
		}
		string request = "INSERT INTO " + table_name + " (" + names + ") VALUES (" + values + ");";
		
		// execute it
		return sqlExecuteQuery( NULL, request, NULL );
	};
	
	bool DogDatabase::sqlCreateTable( const string &table_name, const vector<string> &field_names,
				const vector<string> &field_types, const vector<string> &field_flags )
	{
		// validate lists length
		if ( field_names.size( ) != field_types.size( ) || field_types.size( ) != field_flags.size( ) )
			return false;
			
		// validate table name
		if ( table_name.empty( ) )
			return false;

		// create SQL request
		size_t length = field_names.size( );
		string conc_fields;
		for ( size_t i = 0; i < length; ++i )
		{
			conc_fields += field_names[i] + " " + field_types[i] + " " + field_flags[i];
			if ( i != length - 1 )
				conc_fields += ", ";
		}
		string request = "CREATE TABLE " + table_name + "(" + conc_fields + ");";

		// execute it
		return sqlExecuteQuery( NULL, request, NULL );
	};

	bool DogDatabase::sqlExecuteQuery( int ( *callback )( void*, int, char**, char** ), const string &query, void *output )
	{
		char *zErrMsg = 0;
		
		if ( db == NULL )
		{
			cout << "db is closed, could not execute request!";
			return false;
		}

		cout << "Executing SQL request: " << query << endl;

		int rc = sqlite3_exec( db, query.c_str( ), callback, output, &zErrMsg );
		if ( rc != SQLITE_OK )
		{
			cout << "SQL error: " << zErrMsg << endl;
			sqlite3_free( zErrMsg );
			return false;
		}

		cout << "Executed successfully\n";
		return true;
	};
};
