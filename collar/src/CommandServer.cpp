#include <string>
#include <iostream>

#include <sys/types.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <microhttpd.h>

#include "CommandServer.hpp"

namespace dognetd
{
	CommandServer::CommandServer( int port ):
		port( port ),
		daemon( NULL )
	{ };
	
	CommandServer::~CommandServer( void )
	{
		this->stop( );
	}
	
	bool CommandServer::start( void )
	{
		daemon = MHD_start_daemon( MHD_USE_SELECT_INTERNALLY, port, NULL, NULL, 
			&answer_to_connection, NULL, MHD_OPTION_END );
			
		return daemon != NULL;
	}
	
	void CommandServer::stop( void )
	{
		if ( daemon )
			MHD_stop_daemon( daemon );
	}
	
	int CommandServer::answer_to_connection( void *cls, struct MHD_Connection *connection, 
							  const char *url, 
							  const char *method, const char *version, 
							  const char *upload_data, 
							  size_t *upload_data_size, void **con_cls )
	{
		std::string page( "<html><body>Hello, browser!</body></html>" );
		struct MHD_Response *response;
		int ret;

		response = MHD_create_response_from_buffer (page.length(),
												(void*) page.c_str(), MHD_RESPMEM_MUST_COPY);
		ret = MHD_queue_response (connection, MHD_HTTP_OK, response);
		MHD_destroy_response (response);

		return ret;
	}
};
