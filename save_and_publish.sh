#! /bin/tcsh

set DEBUG = 1

set gitolite_conf = "~/git/gitolite-admin/conf/gitolite.conf"
set gitolite_admin = "~/git/gitolite-admin"

if ($DEBUG) then
	set msg = "debug is ON"
	echo $msg
	repeat $%msg echo -n = 
	echo
endif
	
if (1) then
	
	set commit_msg = "$<"
	set folder = `cat /tmp/cg_pwd`
	set folder_name = $folder:t
	
	if ($DEBUG) then
		echo folder_path: $folder
		echo folder_name: $folder_name
	endif
	
	# switch to folder
	cd $folder
	
	# add all files under the folder
	set git_msg = `git add .`
	if ($DEBUG) then
		echo $git_msg
	endif
	
	# commit
	set git_msg = `git commit -m "$commit_msg"`
	if ($DEBUG) then
		echo $git_msg
	endif
	
	# push to remote
	set git_msg = `git push origin master`
	if ($DEBUG) then
		echo $git_msg
	endif
	
	if ($DEBUG) then
		echo "Done."
	endif
	
endif

exit 0






 