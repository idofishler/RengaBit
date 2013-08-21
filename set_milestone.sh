#! /bin/tcsh

# get script running dir
set cg_folder = ~/.cg

# icon config
set icon_png = "${cg_folder}/file-icon.png"
set change_icon = "${cg_folder}/change_icon.sh"

# usage
if ($# < 2) then
	echo Usage: $0:t file_path commit_msg
	exit 1
endif

set commit_msg = "$2"
set file_path = "$1"
set file_name = "$file_path:t"

# folder handling
if (-d "$file_path") then
	set folder_path = "$file_path"
	set folder = 1
else
	set folder_path = "$file_path:h"
	set folder = 0
endif

cd "$folder_path"

# check if a git repo exists
git status
if ($status) then
	git init .
endif

# git add
if ($folder) then
	# add all file under this folder
	git add .
else
	# add only this file
	git add "$file_path"
endif
	
# change the file/folder's icon
# TODO: check if needed
"$change_icon" "$file_path" "$icon_png"

# git commit
set git_msg = `git commit -m "$commit_msg"`
if ($status) then
	echo "commit issue"
	echo $git_msg
	exit 0 # suppress this error for now
endif

exit 0