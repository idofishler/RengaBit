#! /bin/tcsh

set DEBUG = 1

if ($DEBUG) then
	set msg = "debug is ON"
	echo $msg
	repeat $%msg echo -n = 
	echo
endif
	
rm -f /tmp/cg_pwd
	
if ($DEBUG) then
	echo "Done."
endif
	
exit 0






 