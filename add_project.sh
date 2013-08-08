#! /bin/tcsh

set DEBUG = 1

# gitolite config
set gitolite_conf = "~/git/gitolite-admin/conf/gitolite.conf"
set gitolite_admin = "~/git/gitolite-admin"

# icon config
set icon_png = "/Users/idofishler/Dropbox/Creative Garage/Geeky stuff/Mac client POC/project_folder.png"
set tmp_rsrc = "/tmp/tmpicns.rsrc"

if ($DEBUG) then
	set msg = "debug is ON"
	echo $msg
	repeat $%msg echo -n = 
	echo
endif
	
if (1) then

	set folder = $<
	set folder_name = $folder:t
	
	if ($DEBUG) then
		echo folder_path: $folder
		echo folder_name: $folder_name
	endif
	
	# create repository and set permissions using gitolite
	printf "repo %s\n    RW+\t\t     = @all\n\n" "$folder_name" >> $gitolite_conf
	
	# switch to gitolite_admin folder
	cd $gitolite_admin
	
	# commit changes for gitolite conf
	set git_msg = `git commit -a -m "adding new new project with name: $folder_name"`
	if ($DEBUG) then
		echo $git_msg
	endif
	
	# push gitolite_admin with remote
	set git_msg = `git push`
		if ($DEBUG) then
		echo $git_msg
	endif

	# switch to project folder
	cd $folder
	
	# set clone remote repo to new project folder
	set git_msg = `git clone amazongit:$folder_name .`
	if ($DEBUG) then
		echo $git_msg
	endif
	
	# change the folder icon
	if ($DEBUG) then
		echo "Changing the folder's icon"
	endif
	
	# Take an image and make the image its own icon
	sips -i "$icon_png"
	
	# Extract the icon to its own resource file
	DeRez -only icns "$icon_png" > $tmp_rsrc
	
	# append this resource to the folder's Icon
	set icon = `printf "Icon\r"`
	Rez -append $tmp_rsrc -o $icon
	
	# Use the resource to set the icon.
	SetFile -a C ./
	
	# Hide the Icon\r file from Finder.
	SetFile -a V $icon
	
	if ($DEBUG) then
		echo "Done."
	endif
	
endif

exit 0






 