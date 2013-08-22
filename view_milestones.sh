#! /bin/tcsh

# get script running dir
set cg_folder = ~/.cg

# usage
if ($# < 1) then
	echo Usage: $0:t file_path [rev]
	exit 1
endif

set file_path = "$1"

if ($# == 2) then
	set rev = "$2"
endif

# folder handling
if (-d "$file_path") then
	set file_name = "$file_path"
	set folder_path = "$file_path"
	set folder = 1
else
	set file_name = "$file_path:t"
	set folder_path = "$file_path:h"
	set folder = 0
endif

set ext = "$file_path:e"
set name = "$file_path:t:r"

cd "$folder_path"

# check if a git repo exists
git status
if ($status) then
	echo "No git repo here!"
	${cg_folder}/alert "There are no milestones for this file"
	exit 0
endif

# if this file is being not monitored
set files = `git ls-files "$file_path" --error-unmatch`
if ($status) then
	echo "This file(s) is(are) not being monitored!"
	${cg_folder}/alert "There are no milestones for this file"
	exit 0
endif

# Revert to specific revison if a rev number provided as second arg
# get back to n-th revision by spesifing n
# get back n revision back by specifing -n
if ($?rev) then
	# go back to revision nunber
	if ($rev > 0) then
		set new_rev = `git log --reverse --format=%H -- $file_path | head -$rev | tail -1`
	# go back $rev revison back
	else if ($rev < 0) then
		@ rev *= -1
		set new_rev = "HEAD~$rev"
	endif
	git checkout $new_rev -- "$file_path"
	set commit_msg = `git log $new_rev -n 1 --format=%s -- "$file_path"`
	set commit_msg = "Revert to: $commit_msg"
	git commit -m "$commit_msg" -- "$file_path"
	${cg_folder}/change_file_comment "$file_path" "$commit_msg"
	exit 0
endif
#	===== End Revert to specific revison ====

# prepare a dir to put all milestones
set mls_dir = "$file_path"_milestones
mkdir "$mls_dir"

# copy current file or folder to milestones folder
if ($folder) then
	cp -a "$file_path" "${mls_dir}/${name}_current"
else
	cp -a "$file_path" "${mls_dir}" # for later use (icon issue)
	cp -a "$file_path" "${mls_dir}/${name}_current.${ext}"
endif


# save file's uncommitted changes
git stash

# find revision for this file where the file has been touched
set revs = ( `git log --reverse --format=oneline "$file_path" | cut -d" " -f1` )
set i = 1;
foreach r ($revs)
	# get this file revision
	git checkout $r "$file_path"
	
	# copy revision to the milestones folder
	if ($folder) then
		set new_file_name = "${mls_dir}/${name}_${i}"
	else
		set new_file_name = "${mls_dir}/${name}_${i}.${ext}"
	endif
	cp -a "$file_path" "$new_file_name"

	# modifiy the file comment acorrding to it's commit message
	set comment = `git log --format=oneline -n 1 $r -- "$file_path" | cut -d" " -f2-`
	set commiter_name = `git log $r -n 1 --format=%cn -- "$file_path"`
	${cg_folder}/change_file_comment "$new_file_name" "${commiter_name}: $comment"
 
	# modify the "Date modified" attribute of the file
	set date = `git log $r -n 1 --format=%ci -- "$file_path" | sed 's/\([0-9]*\)-\([0-9]*\)-\([0-9]*\) \([0-9]*\):\([0-9]*\):\([0-9]*\) .*/\1\2\3\4\5.\6/'`
	touch -t $date "$new_file_name"

	# add .cg file meta data
	# <SHA1>-<Commiter Name>-<Date>-<Commit Messege>
	git log $r -n 1 --format="%H-%cn-%ci-%s" -- "$file_path" >> "${mls_dir}/.cg"

	@ i++
end

# clean up...
## get orignal file to the last revision
git checkout HEAD "$file_path"
## and also uncommitted changes if there are any
git stash pop
## fix the icon (for files only)
if (! $folder) then
	mv "${mls_dir}/${file_name}" "./${file_name}"
endif

exit 0