#! /bin/tcsh

set DEBUG = 1

# get script runnig dir
set cg_folder = ~/.cg

# icon config
set icon_png = "${cg_folder}/file-icon.png"
set change_icon = "${cg_folder}/change_icon.sh"

if ($DEBUG) then
	set msg = "debug is ON"
	echo "running scrip $0"
	echo $msg
	repeat $%msg echo -n =
	echo
endif

# usage
if ($# < 1) then
	echo Usage: $0:t commit_msg
	exit 1
endif

set commit_msg = "$1"
set file_path = `cat /tmp/cg_pwd`
set file_name = "$file_path:t"

# folder handling
if (-d $file_path) then
	if ($DEBUG) then
		echo "$file_name is a directory"
	endif
	set folder_path = "$file_path"
	set folder = 1
else
	if ($DEBUG) then
		echo "$file_name is a file"
	endif
	set folder_path = "$file_path:h"
	set folder = 0
endif

# debug printing
if ($DEBUG) then
	echo file_path: $file_path
	echo file_name: $file_name
	echo folder_path: $folder_path
endif

cd $folder_path

# check if a git repo exists
git status
if ($status) then
	git init .
endif

# git add
if ($folder) then
	# add all file under this folder
	git add .
	
	# add only files that are tracked and has been modified
	#set git_msg = `git diff --name-only --diff-filter=M | xargs git add`
	
else
	git add $file_path
endif
	
# change the file/folder's icon
# TODO: check if needed
"$change_icon" "$file_path" "$icon_png"

# git commit
set git_msg = `git commit -m "$commit_msg"`
if ($status) then
	echo "commit issue"
	echo $git_msg
endif

exit 0