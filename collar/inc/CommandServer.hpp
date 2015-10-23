#ifndef COMMANDSERVER_H_
#define COMMANDSERVER_H_

#include <microhttpd.h>

namespace dognetd
{
	// class contains web-server which processes commands from main server
	class CommandServer
	{
		public:
			CommandServer( int port );
			~CommandServer( void );
			bool start( void );
			void stop( void );
			
		private:
			int port;
			struct MHD_Daemon *daemon;
			
			static int answer_to_connection( void *cls, struct MHD_Connection *connection, 
                          const char *url, 
                          const char *method, const char *version, 
                          const char *upload_data, 
                          size_t *upload_data_size, void **con_cls );
	};
}

#endif // COMMANDSERVER_H_
