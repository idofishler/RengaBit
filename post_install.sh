#! /bin/tcsh

# fix pyconfig.h issue on mac osx 10.8
cd /usr
sudo mkdir -p /usr/include
cd /usr/include
sudo ln -sf /System/Library/Frameworks/Python.framework/Versions/2.7/include/python2.7 python2.7
echo "Fixed pyconfig.h issue."

# git for non command line interfaces.
set git = `which git`
set git_path = $git:h
sudo touch /etc/launchd.conf
cat /etc/launchd.conf > ~/.cg/launchd.conf
sudo echo "setenv PATH $git_path" >> ~/.cg/launchd.conf 
sudo mv -f ~/.cg/launchd.conf /etc/
egrep -v '^\s*#' /etc/launchd.conf | launchctl # apply now!
echo "Fixed PATH for non command line apps"

# git global config
set e_user = `git config --get user.name`
if ($#e_user == 0) then
	echo "Please choose a username: "
	set username = $<
	git config --global user.name "$username"
endif
set e_email = `git config --get user.email`
if ($#e_email == 0) then
	echo "Enter you email please: "
	set email = $<
	git config --global user.email "$email"
endif

echo "Thanks for installing RengaBit."
echo "Please restart your computer before using RengaBit."

exit 0
