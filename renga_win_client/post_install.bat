@echo off
echo RengaBit needs your name and email. We do not share your details with anyone.
echo This is a one time thing...
set /p id="Choose user name: " %=%
set /p email="Enter you email please: " %=%
@git config --global user.email "%email%"
@git config --global user.name "%id%"