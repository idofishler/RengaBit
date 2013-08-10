#! /bin/tcsh

set DEBUG = 1

if ($DEBUG) then
	set msg = "debug is ON"
	echo $msg
	repeat $%msg echo -n =
	echo
endif

# usage
if ($# < 1) then
	echo Usage: $0:t path
	exit 1
endif
	
echo $1 > /tmp/cg_pwd
	
if ($DEBUG) then
	echo "Done."
endif
	
exit 0






 