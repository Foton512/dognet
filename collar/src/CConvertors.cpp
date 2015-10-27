//=============================================================================
// Company:
//      Terminal Technologies Ltd
//
// Product:
//      BazeApp
//      Copyright (C) 2010
//=============================================================================

#include "CConvertors.hpp"

#include <math.h>
#include <stdint.h>
#include <string>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits>
#include <sstream>

//years since 1900, so use difference between 2000 and 1900
static const uint8_t kDiffYears = 100;

//=============================================================================
//! Converts a byte containing a value in a numeric format to a corresponding
//! decimal value.
//! A byte in a numeric format can only have its most and least significant nimbles
//! to be in a range from 0 to 9 (digital numbers).
//! Function returns true if conversion succeeded, and false if an invalid digit is
//! encountered
//=============================================================================
bool CConvertors::bcd2bin(char bcd_byte, char& bin)
{
	int left_digit = (bcd_byte >> 4) & 0x0000000f;
	if (left_digit > 9)
	{
		return false;
	}

	left_digit *= 10;
	int right_digit = bcd_byte & 0x0000000f;
	if (right_digit > 9)
	{
		return false;
	}

	bin = left_digit + right_digit;

	return true;
}

//=============================================================================
// returns amount with dot
//=============================================================================
std::string CConvertors::amountWithDot(std::string amount, int point_pos)
{
	if (point_pos == 0) return amount;

	std::string minus_append;
	if (!amount.empty() && amount[0] == '-')
	{
		minus_append = '-';
		amount.erase(0, 1);
	}

	int amount_len = amount.length();

	if (amount_len <= point_pos)
	{
		amount = std::string(point_pos - amount_len + 1, '0') + amount;
	}

	amount_len = amount.length();
	return minus_append + amount.substr(0, amount_len - point_pos) + "." +
			amount.substr(amount_len - point_pos, amount_len);
}

//=============================================================================
//! Converts string of bcd chars to binary value
//!
//! Example: 998877 -> F3DDD
//!
//! \param bcd_str String of BCD values (MSB on left)
//! \param bin Reference to store Binary value of BCD string
//!
//! \return true if successful otherwise false
//=============================================================================
bool CConvertors::bcd2bin(const std::string& bcd_str, int& bin)
{
	// check bcd_str for empty and size
	if (bcd_str.empty())
	{
		return false;
	}

	//FF on all bytes mean that field not set
	if (bcd_str.find_first_not_of("\xFF") == std::string::npos)
	{
		bin = std::numeric_limits<uint32_t>::max();
		return true;
	}

	uint32_t i = 0;
	char temp = 0;
	uint8_t bcd_byte = 0;
	bin = 0;

	while (i < bcd_str.size())
	{
		bcd_byte = static_cast<uint8_t>(bcd_str[i]);

		// 0xFF - not filled both semi-bytes
		if (bcd_byte == 0xFF)
		{
			// Check that remaining bytes are FF's
			return (bcd_str.find_first_not_of("\xFF", i+1) == std::string::npos);
		}
		// 0xXF - not filled last semi-byte
		else if ((bcd_byte & 0x0F) == 0x0F)
		{
			temp = static_cast<char>(bcd_byte >> 4);
			if (temp > 9 )
			{
				return false;
			}
			bin *= 10;
			bin += temp;
			// Check that remaining bytes are FF's
			return (bcd_str.find_first_not_of("\xFF", i+1) == std::string::npos);
		}
		else if (!bcd2bin(bcd_str[i], temp))
		{
			return false;
		}
		bin *= 100;
		bin += temp;
		i++;
	}

	return true;
}

//=============================================================================
//! Converts DDMMYY bcd date to expiry date as time_t
//=============================================================================
bool CConvertors::bcdDDMMYY2ExpiryDatet(const std::string& bcd_str, int & expiry_date)
{
	char day = 0;
	char mon = 0;
	char year = 0;

	if (bcd_str.length() < 3 ||
			!bcd2bin(bcd_str[0], day) ||
			!bcd2bin(bcd_str[1], mon) ||
			!bcd2bin(bcd_str[2], year))
	{
		return false;
	}

	--mon;
	year = (year<50)? year + kDiffYears : year;

	struct tm date_tm;
	memset(&date_tm, 0, sizeof(date_tm));

	date_tm.tm_mday = day;
	date_tm.tm_mon = mon;
	date_tm.tm_year = year;

	date_tm.tm_hour = 23;
	date_tm.tm_min = 59;
	date_tm.tm_sec = 59;

	expiry_date = mktime(&date_tm);

	if (expiry_date == -1 ||
			date_tm.tm_mday != day ||
			date_tm.tm_mon != mon ||
			date_tm.tm_year != year)
	{
		//invalid expiry date
		return false;
	}

	return true;
}

//=============================================================================
//! Convert date from string representation (YYMMDD) to int (time_t)
//=============================================================================
int CConvertors::strYYMMDD2datet(const std::string & YYMMDD)
{
	std::string date = YYMMDD;
	date.resize(6, '0');

	struct tm td;
	memset(&td, 0, sizeof(td));

	int year = CConvertors::str2int(date.substr(0, 2));
	int month = CConvertors::str2int(date.substr(2, 2));
	int day = CConvertors::str2int(date.substr(4, 2));

	//fill struct tm
	td.tm_mday = day;
	td.tm_mon = month - 1;
	td.tm_year = (year<50)? year + kDiffYears : year;

	int date_t = mktime(&td);
	if (date_t != -1 &&
			day == td.tm_mday &&
			month == td.tm_mon + 1 &&
			year == td.tm_year - kDiffYears)
	{
		return date_t;
	}

	return 0;
}

//=============================================================================
//! Convert time from string representation (HHMMSS) to int (time_t)
//=============================================================================
int CConvertors::strHHMMSS2datet(const std::string & HHMMSS)
{
	std::string date = HHMMSS;
	date.resize(6, '0');

	int hour = CConvertors::str2int(date.substr(0, 2));
	int min = CConvertors::str2int(date.substr(2, 2));
	int sec = CConvertors::str2int(date.substr(4, 2));

	return hour * 3600 + min * 60 + sec;
}

//=============================================================================
//! Convert time/date from string representation (YYMMDDHHMMSS) to int (time_t)
//=============================================================================
int CConvertors::strYYMMDDHHMMSS2datet(const std::string & str)
{
	std::string date = str;
	date.resize(12, '0');

	int year = CConvertors::str2int(date.substr(0, 2));
	int month = CConvertors::str2int(date.substr(2, 2));
	int day = CConvertors::str2int(date.substr(4, 2));

	int hour = CConvertors::str2int(date.substr(6, 2));
	int min = CConvertors::str2int(date.substr(8, 2));
	int sec = CConvertors::str2int(date.substr(10, 2));

	struct tm tm;
	memset(&tm, 0, sizeof(tm));

	//fill struct tm
	tm.tm_mday = day;
	tm.tm_mon = month - 1;
	tm.tm_year = (year<50)? year + kDiffYears : year;

	tm.tm_hour = hour;
	tm.tm_min = min;
	tm.tm_sec = sec;

	return mktime(&tm);
}

//=============================================================================
//! Convert string representation of date (YYMM) to expiry date as int (time_t)
//=============================================================================
int CConvertors::strYYMM2ExpiryDatet(const std::string & YYMM)
{
	if (YYMM.length() < 4)
	{
		return 0;
	}

	struct tm td;
	memset(&td, 0, sizeof(td));

	int year = CConvertors::str2int(YYMM.substr(0, 2));
	int month = CConvertors::str2int(YYMM.substr(2, 2));

	// card is expired when next month begins
	++month;
	int day = 1;

	//fill struct tm
	td.tm_mday = day;
	td.tm_mon = month - 1;
	td.tm_year = (year<50)? year + kDiffYears : year;


	int date_t = mktime(&td);

	if (date_t > 0)
	{
		return date_t - 1;
	}

	return 0;
}

//=============================================================================
//! Convert time to formatted string
//=============================================================================
std::string CConvertors::datet2str(int time, const std::string & format_mask)
{
	struct tm tm_time;
	gmtime_r(reinterpret_cast< time_t * >( &time ), &tm_time);

	char buf_time[100];
	if (!strftime(buf_time, sizeof(buf_time)-1, format_mask.c_str(), &tm_time))
	{
		return std::string();
	}
	return std::string(buf_time);
}

//=============================================================================
//! Convert int to string
//=============================================================================
std::string CConvertors::int2str(int val)
{
	char buffer[20];
	// long int used like in std::iostream
	sprintf(buffer, "%d", val);
	return std::string(buffer);
}

//=============================================================================
//! Convert unsigned int to string
//=============================================================================
std::string CConvertors::uint2str(unsigned int val)
{
	char buffer[20];
	// long int used like in std::iostream
	sprintf(buffer, "%u", val);
	return std::string(buffer);
}

//=============================================================================
//! Convert string to int
//=============================================================================
int CConvertors::str2int(const std::string & str)
{
	int result = 0;
	sscanf(str.c_str(), "%d", &result);
	return result;
}

//=============================================================================
//! Convert string to unsigned int
//=============================================================================
unsigned int CConvertors::str2uint(const std::string & str)
{
	unsigned int result = 0;
	sscanf(str.c_str(), "%u", &result);
	return result;
}

//=============================================================================
//! Convert string to int with checking
//=============================================================================
bool CConvertors::str2int(const std::string & val, int & result)
{
	int scanf_count = sscanf(val.c_str(), "%d", &result);
	return scanf_count == 1;
}

//=============================================================================
//! Convert string to unsigned int with checking
//=============================================================================
bool CConvertors::str2uint(const std::string & val, unsigned int & result)
{
	int scanf_count = sscanf(val.c_str(), "%u", &result);
	return scanf_count == 1;
}

//=============================================================================
//! Convert string to int64_t
//=============================================================================
int64_t CConvertors::str2int64(const std::string& str)
{
	int64_t result = 0;
	sscanf(str.c_str(), "%lld", &result);
	return result;
}

//=============================================================================
//! Convert int64_t to string
//=============================================================================
std::string CConvertors::int642str(const int64_t value)
{
	char buffer[28];
	sprintf(buffer, "%lld", value);
	std::string result(buffer);
	return result;
}

//=============================================================================
//! Convert mem buffer to integer
//=============================================================================
bool CConvertors::mem2int(const std::string & str, int & value)
{
	value = 0;

	if (str.size() > sizeof(int))
	{
		return false;
	}

	for (size_t pos = 0; pos < str.size(); ++pos)
	{
		value = (value << 8) + static_cast<uint8_t>(str[pos]);
	}

	return true;
}

//=============================================================================
//! Returns t in degree k
//=============================================================================
int CConvertors::power(int t, int k)
{
	int res = 1;

	while (k)
	{
		if (k & 1) res *= t;
		t *= t;
		k >>= 1;
	}
	return res;
}

//=============================================================================
//! Converts integer binary value to string representation (MSB on left)
//!
//! \param bin Integer binary value
//! \param str String representation of binary value
//!
//! \return true if successfull otherwise false
//=============================================================================
bool CConvertors::int2mem(int bin, std::string& str)
{
	uint32_t i = 0;
	str.clear();
	while (i < sizeof(bin))
	{
		str.insert(0, 1, static_cast<char> (0xFF & (bin >> (i * 8))));
		i++;
	}

	return true;
}

//=============================================================================
// Converts ASCII string to int value
//=============================================================================
bool CConvertors::ASCII2int(const std::string& str, int &bin)
{
	bin = 0;
	size_t left = str.find_first_not_of(std::string(" \x00", 2));
	size_t right = str.find_last_not_of(std::string(" \x00", 2));

	for (size_t i = left; i <= right; ++i)
	{
		if ((str[i] > '9') || (str[i] < '0'))
		{
			bin = 0;
			return false;
		}

		bin = bin * 10 + str[i] - '0';
	}

	return true;
}

//=============================================================================
// // Converts string in hex to int
//=============================================================================
bool CConvertors::hex2int(const std::string & hex, unsigned int & result)
{
	char garbage;
	int scanf_count = sscanf(hex.c_str(), "%X%c", &result, &garbage);
	return scanf_count == 1;
}

//=============================================================================
// // Converts int to string in hex
//=============================================================================
std::string CConvertors::int2hex(unsigned int val)
{
	char buf[10];
	sprintf(buf, "%02X", val);
	return std::string(buf);
}

//=============================================================================
//! Converts string of binary value to string of hex value
//!
//! \param buf String representation of binary value
//! \return string of hex value
//=============================================================================
std::string CConvertors::bin2hex(const std::string& buf)
{
	std::string hbuf;
	char cbuf[4];

	for (size_t i = 0; i < buf.size(); ++i)
	{
		sprintf(cbuf, "%02x", (uint8_t)buf[i]);
		hbuf.append(cbuf, 2);
	}

	return hbuf;
}

//=============================================================================
std::string CConvertors::bin2hex(const int bin)
{
	int bin_buf = bin;
	std::string hex = "";

	if (bin_buf == 0)
	{
		return "0";
	}

	while (bin_buf > 0)
	{
		hex.insert(0, 1, (bin_buf % 10) + '0');
		bin_buf /= 10;
	}

	return hex;
}

//=============================================================================
//! Converts string of hex value to string of binary value
//!
//! \param hex_buf String representation of hex value
//! \return string of binary value
//=============================================================================
std::string CConvertors::hex2bin(const std::string& hex_buf)
{
	std::string bin_buf;
	char bin;

	size_t buf_size = hex_buf.size();

	for (size_t i = 0; i < buf_size; i += 2)
	{
		if (buf_size - i >= 2)
		{
			sscanf(&hex_buf[i], "%02hhx", &bin);
		}
		else
		{
			sscanf(&hex_buf[i], "%01hhx", &bin);
		}

		bin_buf.append(1, bin);
	}

	return bin_buf;
}

//=============================================================================
//! Converts deciman value to numeric byte
//!
//! \param DecimalVal representation of decimal value
//! \param NumericByte Pointer to store of numeric byte
//! \return true if successfull otherwise false
//=============================================================================
bool CConvertors::decimal2NumericByte(uint8_t DecimalVal, char *NumericByte)
{
	int val = 0x000000FF & DecimalVal;
	if (val < 10)
		*NumericByte = DecimalVal;
	else
		if (val >= 10 && val <= 99)
		{
			int dec = val / 10;
			*NumericByte = ((dec) << 4);
			*NumericByte |= (val - dec * 10);
		}
		else
			return false;
	return true;
}

//=============================================================================
//! Converts binary value to bcd chars
//!
//! \param bin representation of binary value
//! \param bcd_str Pointer to store of bcd chars
//! \return true if successfull otherwise false
//=============================================================================
/*
bool CConvertors::bin2bcd(int bin, std::string& bcd_str)
{
	std::ostringstream o;
	o << bin;
	std::string t = o.str();

	if (t.size() % 2) t.insert(0, 1, '0');
	bcd_str = hex2bin(t);
	return true;
}
//*/

//=============================================================================
//! Converts binary value to bcd char
//!
//! \param bin representation of binary value
//! \return bcd value
//=============================================================================
char CConvertors::bin2bcd(const char bin)
{
	return ( ( ( bin % 100 ) / 10 ) << 4 ) + ( bin % 10 );
}

//=============================================================================
//! Converts binary value to bcd chars
//!
//! \param bin representation of binary value
//! \param bcd_str Pointer to store of bcd chars
//! \return true if successfull otherwise false
//=============================================================================
bool CConvertors::bin2bcd(int bin, std::string* bcd_str)
{
	std::string t = CConvertors::int2str(bin);

	if (t.size() % 2)
	{
		t.insert(0, 1, '0');
	}

	*bcd_str = hex2bin(t);
	return true;
}

//=============================================================================
// Converts powered binary value to bcd chars
//=============================================================================
std::string CConvertors::int2EMVLimit(int bin, unsigned int power)
{
	std::string t = CConvertors::int2str(bin);

	if (power)
	{
		t.append(power, '0');
	}

	if (t.size() < 12)
	{
		t.insert(0, 12 - t.size(), '0');
	}

	return hex2bin(t);
}

//=============================================================================
//! Serialize string chars to hex chars for sql query BLOB
//!
//! \param str String for serialization
//!
//! \return hex string
//=============================================================================
std::string CConvertors::strToBLOB(const std::string &str)
{
	return "x'" + bin2hex(str) + "'";
}

// Converts string of hex value to string of bcd value
std::string CConvertors::hex2bcd(const std::string &hex_buf)
{
	bool addZero = false;
	std::string bcd_buf;
	unsigned char high, low;

	bcd_buf.clear();

	if (hex_buf.size() % 2 == 1)
	{
		addZero = true;
	}

	for (size_t i = 0; i < hex_buf.size(); i += 2)
	{
		if (addZero)
		{
			bcd_buf.push_back(hex_buf[i] - '0');
			--i;
			addZero = false;
		}
		else
		{
			high = (hex_buf[i] - '0') * 16;
			low = hex_buf[i + 1] - '0';
			bcd_buf.push_back(high + low);
		}
	}

	return bcd_buf;
}

// converts string of ASCII chars to string of hex
std::string CConvertors::str2hex(const std::string &str_buf)
{
	std::string hex_buf;
	unsigned char high, low;
	unsigned char symb;

	for (size_t i = 0; i < str_buf.size(); i += 2)
	{
		// Gen high nibble
		symb = str_buf[i];
		if ( symb < '0' )
			high = 0;
		else if ( symb < ':' )
			high = (symb - '0');
		else if ( symb < 'A' )
			high = 0;
		else if ( symb < 'G' )
			high = (symb - '7');
		else
			high = 0;
		high = high * 16;

		// Gen low nibble
		symb = str_buf[i + 1];
		if ( symb < '0' )
			low = 0;
		else if ( symb < ':' )
			low = (symb - '0');
		else if ( symb < 'A' )
			low = 0;
		else if ( symb < 'G' )
			low = (symb - '7');
		else
			low = 0;

		hex_buf.push_back(high + low);
	}

	return hex_buf;
}

// Converts string of bcd value to string of hex value
std::string CConvertors::bcd2hex(const std::string &bcd_buf)
{
	std::string hex_buf;
	unsigned char hex = 0;

	hex_buf.clear();

	for (size_t i = 0; i < bcd_buf.size(); ++i)
	{
		hex = ((bcd_buf[i] & 0xf0) >> 4);
		if( hex < 10 )
			hex_buf.append(1, hex + '0');
		else
			hex_buf.append(1, hex - 10 + 'A');


		hex = ((bcd_buf[i] & 0x0f) >> 0);
		if( hex < 10 )
			hex_buf.append(1, hex + '0');
		else
			hex_buf.append(1, hex - 10 + 'A');
	}

	return hex_buf;
}

// Converts array of bcd chars to string
std::string CConvertors::bcd2hex(const char *bcd, const size_t bcd_len)
{
	std::string hex_buf;
	unsigned char hex = 0;

	hex_buf.clear();

	for (size_t i = 0; i < bcd_len; ++i)
	{
		hex = ((bcd[i] & 0xf0) >> 4);
		if( hex < 10 )
			hex_buf.append(1, hex + '0');
		else
			hex_buf.append(1, hex - 10 + 'A');


		hex = ((bcd[i] & 0x0f) >> 0);
		if( hex < 10 )
			hex_buf.append(1, hex + '0');
		else
			hex_buf.append(1, hex - 10 + 'A');
	}

	return hex_buf;
}

// Converts string of hex value to string of bcd left justified value
std::string CConvertors::hex2bcdleft(const std::string &hex_buf)
{
	std::string bcd_buf;
	unsigned char high, low;

	for (size_t i = 0; i < hex_buf.size(); i += 2)
	{
		if (i == hex_buf.size() - 1)
		{
			high = (hex_buf[i] - '0') * 16;
			low = 0x0f;
			bcd_buf.push_back(high + low);
		}
		else
		{
			high = (hex_buf[i] - '0') * 16;
			low = hex_buf[i + 1] - '0';
			bcd_buf.push_back(high + low);
		}
	}

	return bcd_buf;
}

// Converts string of bcd left justified value to string of hex value
std::string CConvertors::bcdleft2hex(const char *bcd, const size_t bcd_len)
{
	std::string hex_buf;

	hex_buf.clear();

	for (size_t i = 0; i < bcd_len; ++i)
	{
		char nibble = (bcd[i] & 0xf0) >> 4;
		if (nibble == 0x0f)
		{
			return hex_buf;
		}
		hex_buf.append(1, nibble + '0');

		nibble = bcd[i] & 0x0f;
		if (nibble == 0x0f)
		{
			return hex_buf;
		}
		hex_buf.append(1, nibble + '0');
	}

	return hex_buf;
}

// Cut tails of long strings and add leading characters to short ones
void CConvertors::frontResizeString(std::string *str, const size_t size, const char filler)
{
	if (str->length() > size)
	{
		str->resize(size);
	}
	else
	{
		str->insert(0, size - str->length(), filler);
	}
}

// Cut leading sequence of specified symbol from the string
void CConvertors::frontTrimString(std::string *str, const std::string &symbols_to_be_cut)
{
	size_t start_pos = str->find_first_not_of(symbols_to_be_cut);
	if (start_pos == std::string::npos)
	{
		str->clear();
	}
	else
	{
		str->erase(0, start_pos);
	}
}

// Cut trailing sequence of specified symbol from the string
void CConvertors::backTrimString(std::string *str, const std::string &symbols_to_be_cut)
{
	size_t start_pos = str->find_last_not_of(symbols_to_be_cut);
	if (start_pos == std::string::npos)
	{
		str->clear();
	}
	else
	{
		str->erase(start_pos + 1);
	}
}

// converts string with percent encoded symbols to regular string
std::string CConvertors::parsePercentEncoding(const std::string & pos_str)
{
	std::string result = pos_str;
	unsigned int curr_pos = 0;

	while ((curr_pos = result.find('%', curr_pos)) != std::string::npos)
	{
		if (result.size() - curr_pos < 3)
		{
			++curr_pos;

			continue;
		}

		std::string symb = hex2bin(result.substr(curr_pos + 1, 2));

		result.replace(curr_pos, 3, symb);
	}

	return result;
}


short CConvertors::get_max_day(int month, int year)
{
	if(month == 1 || month == 3 || month == 5 || month == 7 || month == 8 || month == 10 || month == 12)
	{
		return 31;
	}
	else if(month == 4 || month == 6 || month == 9 || month == 11)
	{
		return 30;
	}
	else
	{
		if(year % 4 == 0)
		{
			if(year % 100 == 0)
			{
				if(year % 400 == 0)
					return 29;
				return 28;
			}
			return 29;
		}
		return 28;
	}
}

std::vector<std::string> CConvertors::split( const std::string &s, char delim )
{
	std::vector<std::string> elems;
	std::stringstream ss( s );
	std::string item;
	while ( getline( ss, item, delim ) )
	{
		elems.push_back( item );
	}
	return elems;
}

double CConvertors::str2double( const std::string &s )
{
	return atof( s.c_str( ) );
}
