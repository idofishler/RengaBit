#! /bin/tcsh

# get script running dir
set cg_folder = ~/.cg
set traker_url = "http://announce.torrentsmd.com:6969/announce"
set maketorrent = ${cg_folder}/BitTorrent/btmakemetafile.py
set send_mail = ${cg_folder}/send_mail_with_file.py

# usage
if ($# < 2) then
	echo Usage: $0:t recipient_email file_path
	exit 1
endif

set recipient_email = "$1"
set file_path = "$2"
set sender_email = "mailer@rengabit.com"

set file_name = "$file_path:t"
set renga_folder = "$file_path:h"/.renga
set renga_file = ${renga_folder}/${file_name}.renga

# create the .renga folder if not exists
if (! -e "$renga_folder") then
	mkdir "$renga_folder"
endif

# create the torrent file
$maketorrent $file_path $traker_url

# send it via mail
#$send_mail -f "$renga_file" -s "$sender_email" -r "$recipient_email"

# sarat sharing the file


exit 0