/*******************************************************************************
 * gpuATTRACT framework
 * Copyright (C) 2015 Uwe Ehmann
 *
 * This file is part of the gpuATTRACT framework.
 *
 * The gpuATTRACT framework is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * The gpuATTRACT framework is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *******************************************************************************/
#define LOGGER_SRC

#include "asUtils/Logger.h"

namespace Log {

Logger *global_log;

Logger::Logger(logLevel level, std::ostream *os)
: _log_level(level), _msg_log_level(Log::Error), _do_output(true), _filename(""),
  _log_stream(os), logLevelNames(), _starttime(), _rank(0) {
	init_starting_time();
	this->init_log_levels();
#ifdef ENABLE_MPI
	MPI_Comm_rank(MPI_COMM_WORLD, &_rank);
#endif
}


Logger::Logger(logLevel level, std::string prefix) :  _log_level(level), _msg_log_level(Log::Error),
		_do_output(true), _filename(""), _log_stream(0), logLevelNames(), _starttime(), _rank(0) {
	init_starting_time();
	this->init_log_levels();
	std::stringstream filenamestream;
	filenamestream << prefix;
#ifdef ENABLE_MPI
	MPI_Comm_rank(MPI_COMM_WORLD, &_rank);
	filenamestream << "_R" << _rank;
#endif
	filenamestream << ".log";
	_filename = filenamestream.str();
	_log_stream = new std::ofstream(_filename.c_str());
}

Logger::~Logger() {
	*_log_stream << std::flush;
	if (_filename != "")
		(static_cast<std::ofstream*> (_log_stream))->close();
}


/// allow logging only for a single process
bool Logger::set_mpi_output_root(int root) {
	if (_rank != root)
		_do_output = false;
	return _do_output;
}

/// all processes shall perform logging
bool Logger::set_mpi_output_all() {
	_do_output = true;
	return _do_output;
}

/// allow a set of processes for logging
bool Logger::set_mpi_output_ranks(int num_nums, int* nums) {
	int i;
	for(i = 0; i < num_nums; i++)
		if (nums[i] == _rank)
			_do_output = true;
	return _do_output;
}

} /* end namespace Log */
