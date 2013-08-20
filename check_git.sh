#! /bin/tcsh

set DEBUG = 0

if ($DEBUG) then
	set msg = "debug is ON"
	echo $msg
	repeat $%msg echo -n =
	echo
endif

set git_msg = `agit --version`

if ($status) then
	echo "git is not installed"
	exit 1
endif

echo "git is installed"
exit 0