#! /bin/tcsh

# get script running dir
set cg_folder = ~/.cg
set meta_file_name = ".cg"

# icon config
set icon_png = "${cg_folder}/file-icon.png"
set change_icon = "${cg_folder}/change_icon.sh"

# usage
if ($# < 1) then
	echo Usage: $0:t file_path
	exit 1
endif

set file_path = "$1"
set mls_folder = "$file_path:h"
set org_file_folder = "$mls_folder:h"

cd "$mls_folder"

set rev_num = `echo "$file_path" | sed 's/.*_\([0-9]*\).*/\1/'`
set org_file_name = `echo "$file_path" | sed 's/.*\(\/.*\)_[0-9]*\(.*\)/\1\2/'`
set org_file_path = "${org_file_folder}${org_file_name}"

# check if .cg exist
if (! -e $meta_file_name) then
	echo "no $meta_file_name meta file here"
	${cg_folder}/alert "This is not a milestome of any file or folder"
	exit 0
endif

# get the rev sha1 from the meta file
set rev = `cat $meta_file_name | head -$rev_num | tail -1 | cut -d"-" -f1`

git checkout $rev -- "$org_file_path"
set commit_msg = `git log $rev -n 1 --format=%s -- "$org_file_path"`
set commit_msg = "Revert to: $commit_msg"
git commit -m "$commit_msg" -- "$org_file_path"
${cg_folder}/change_file_comment "$org_file_path" "$commit_msg"

# change the file/folder's icon
"$change_icon" "$org_file_path" "$icon_png"

# delete the milestones folder
rm -rf "$mls_folder"

exit 0