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

# change the file icon
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
	
# Extract the icon to its own resource file
DeRez -only icns "$icon_png" > $tmp_rsrc

if (-d $file_name) then
	if ($DEBUG) then
		echo "file is a directory"
	endif
	cd "$file_name"
	# append this resource to the folder's Icon
	set icon = `printf "Icon\r"`
else
	set icon = "$file_name"
endif
	
# append this resource to the file we want to icon-ize.
if ($DEBUG) then
	echo appending resource to "$icon"
endif
Rez -append $tmp_rsrc -o $icon
	
# Use the resource to set the icon.
if ($DEBUG) then
	echo "Using the resource to set the icon"
endif
if (-d $file_name) then
	SetFile -a C ./
else
	SetFile -a C "$file_name"
endif

# Hide the Icon\r file from Finder in case of a folder.
if (-d $file_name) then
	if ($DEBUG) then
		echo "hiding the Icon file"
	endif
	SetFile -a V $icon
endif
	
if ($DEBUG) then
	echo "Done."
endif