#! /bin/tcsh

set DEBUG = 1

# icon config
set icon_png = "/Users/idofishler/Dropbox/Creative Garage/Design/Milestone/file-icon2.png"
set change_icon = "/Users/idofishler/Dropbox/Creative Garage/Geeky stuff/Mac client POC/change_icon.sh"

if ($DEBUG) then
	set msg = "debug is ON"
	echo "running scrip $0"
	echo $msg
	repeat $%msg echo -n = 
	echo
endif

if (1) then

	set commit_msg = "$<"
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
	git commit -m "$commit_msg"
	
endif

exit 0