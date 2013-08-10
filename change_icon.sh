#! /bin/tcsh

set DEBUG = 1

set tmp_rsrc = "/tmp/tmpicns.rsrc"

if ($DEBUG) then
	echo "running scrip $0"
	set msg = "debug is ON"
	echo $msg
	repeat $%msg echo -n =
	echo
endif

# usage
if ($# < 2) then
	echo Usage: $0:t file_name icon_file.png
	exit 1
endif

set file_name = "$1"
set icon_png = "$2"
  	
if ($DEBUG) then
	echo "Changing $1 icon using $2"
endif
	
# Take an image and make the image its own icon
sips -i "$icon_png"

# set the icon
~/.cg/seticon "$icon_png" "$file_name"

exit 0