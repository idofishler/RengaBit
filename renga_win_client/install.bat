@echo off
@REGEDIT.EXE "C:\Rengabit\rengaReg.reg"
set /p id="Choose user name: " %=%
set /p email="Enter you email please: " %=%
@git config --global user.email "%email%"
@git config --global user.name "%id%"