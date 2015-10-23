#ifndef CCONVERTORS_H_
#define CCONVERTORS_H_

#include <stdint.h>
#include <string>
#include <vector>

//=============================================================================
//! Class contains collection of functions for converts data
//=============================================================================
class CConvertors
{
	public:
		// Convert int to string
		static std::string int2str(int val);

		// Convert unsigned int to string
		static std::string uint2str(unsigned int val);

		// Convert string to int
		static int str2int(const std::string & str);

		// Convert string to unsigned int
		static unsigned int str2uint(const std::string & str);

		// Convert string to int.
		// Return true if converting was successfully otherwise false
		static bool str2int(const std::string & val, int & result);

		// Convert string to unsigned int.
		// Return true if converting was successfully otherwise false
		static bool str2uint(const std::string & val, unsigned int & result);

		// returns amount with dot
		static std::string amountWithDot(std::string amount, int point_pos);

		// Convert date from string representation (YYMMDD) to int (time_t)
		static int strYYMMDD2datet(const std::string & YYMMDD);

		// Convert time from string representation (HHMMSS) to int (time_t)
		static int strHHMMSS2datet(const std::string & HHMMSS);

		// Convert time/date from string representation (YYMMDDHHMMSS) to int (time_t)
		static int strYYMMDDHHMMSS2datet(const std::string & str);
		
		// Convert string representation of date (YYMM) to expiry date as int (time_t)
		static int strYYMM2ExpiryDatet(const std::string & YYMM);

		// Convert time to formatted string
		static std::string datet2str(int time, const std::string & format_mask);

		// Convert mem buffer to integer
		static bool mem2int(const std::string & str, int & value);

		// Returns t in degree k
		static int power(int t, int k);

		// Converts a byte containing a value in a numeric format to a corresponding decimal value.
		static bool bcd2bin(char bcd_byte, char& bin);

		// Converts string of bcd chars to binary value
		static bool bcd2bin(const std::string& bcd_str, int& bin);

		// Converts DDMMYY bcd date to expiry date as time_t
		static bool bcdDDMMYY2ExpiryDatet(const std::string& bcd_str, int & expiry_date);

		// Converts binary value to bcd char
		static char bin2bcd(const char bin);

		// Converts binary value to bcd chars
		static bool bin2bcd(int bin, std::string* bcd_str);

		// Converts integer binary value to string representation (MSB on left)
		static bool int2mem(int bin, std::string& str);

		// Converts ASCII string to int value
		static bool ASCII2int(const std::string& str, int &bin);

		// Converts string in hex to int
		static bool hex2int(const std::string & hex, unsigned int & result);

		// Converts int to string in hex
		static std::string int2hex(unsigned int val);

		// Converts powered binary value to bcd chars
		static std::string int2EMVLimit(int bin, unsigned int power);

		// Converts string of binary value to string of hex value
		static std::string bin2hex(const std::string& buf);

		// Converts binary value to string of hex value
		static std::string bin2hex(const int bin);

		// Converts string of hex value to string of binary value
		static std::string hex2bin(const std::string& buf);

		// Converts string of hex value to string of bcd value
		static std::string hex2bcd(const std::string &hex_buf);

		// converts string of ASCII chars to string of hex
		static std::string str2hex(const std::string &str_buf);

		// Converts string of bcd value to string of hex value
		static std::string bcd2hex(const std::string &bcd_buf);

		// Converts array of bcd chars to string
		static std::string bcd2hex(const char *bcd, const size_t bcd_len);

		// Converts string of hex value to string of bcd left justified value
		static std::string hex2bcdleft(const std::string &hex_buf);

		// Converts string of bcd left justified  value to string of hex value
		static std::string bcdleft2hex(const char *bcd, const size_t bcd_len);

		// Converts deciman value to numeric byte
		static bool decimal2NumericByte(uint8_t DecimalVal, char *NumericByte);

		// serialize string chars to hex chars for sql query BLOB
		static std::string strToBLOB(const std::string &str);

		// convert cp866 string to koi8-r
		static std::string convertCp866ToKoi8R(const std::string &cp866_str);

		// convert cp866 string to cp1251
		static std::string convertCp866ToCp1251(const std::string &cp866_str);

		// convert string to int64_t
		static int64_t str2int64(const std::string& str);

		// convert int64_t to string
		static std::string int642str(const int64_t value);

		// cut tails of long strings and add leading characters to short ones
		static void frontResizeString(std::string *str, const size_t size, const char filler);

		// cut leading sequence of specified symbol from the string
		static void frontTrimString(std::string *str, const std::string &symbols_to_be_cut);

		// cut trailing sequence of specified symbol from the string
		static void backTrimString(std::string *str, const std::string &symbols_to_be_cut);

		// converts string with percent encoded symbols to regular string
		static std::string parsePercentEncoding(const std::string & pos_str);

		static short get_max_day(int month, int year);

	private:
		// private constructor
		CConvertors();
};

#endif // CCONVERTORS_H_
