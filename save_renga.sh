#! /bin/tcsh

# get script running dir
set cg_folder = ~/.cg

# usage
if ($# < 2) then
	echo Usage: $0:t traget_folder renga_file
	exit 1
endif

set traget_folder = "$1"
set renga_file = "$2"

java -jar ${cg_folder}/ttorrent-1.3-SNAPSHOT-shaded.jar -o "$traget_folder" "$renga_file"

exit 0