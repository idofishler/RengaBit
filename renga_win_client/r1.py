import os
import sys
import subprocess

base="C:\\Users\AlmondNET\\AppData\Local\\GitHub\\PortableGit_015aa71ef18c047ce8509ffb2f9e4bb0e3e73f13\\"
baseScript="C:\\Users\AlmondNET\\AppData\Local\\GitHub\\PortableGit_015aa71ef18c047ce8509ffb2f9e4bb0e3e73f13\\r1.bat"

def checkAndCreateRepo(directory,file):
        #check if repo exists
    try:
        res=subprocess.check_output([baseScript,directory,"nf","git status"])
        #print(res)
    except:
        #no repo , need to create one
        res=subprocess.check_output([baseScript,directory,"nf","git init"])
        #print(res)

def markMileStone(directory,file):
    try:
        checkAndCreateRepo(directory,file)
        res=subprocess.check_output([baseScript,directory,"nf","git add "+file])
        #print(res)
        print("Enter Commit note")
        commitNote=input()
        print(commitNote)
        res=subprocess.check_output([baseScript,directory,"nf","git commit -m \""+commitNote+"\" "+file])
        print(res)
    except Exception as inst:
        print(type(inst))     # the exception instance
        print(inst.args)      # arguments stored in .args
        print (inst)           # __str__ allows args to printed directly

def showMilestone(directory,file):
    try:
        try:
            res=subprocess.check_output([baseScript,directory,"nf","git status"])
        #print(res)
        except:
            #no repo , exit
            print("no repo was found for this file ")
            return
        res=subprocess.check_output([baseScript,directory,"nf","git log --reverse --format=%H,%an,%at,%s "+file])
        vA=res.decode("utf-8").rstrip().split("\n")
        if not (os.path.isdir(file+"-Milestones")):
            os.makedirs(file+"-Milestones")
        for version in vA:
            vData=version.split(",")
            hashC=vData[0]
            commiter=vData[1]
            date=vData[2]
            subject=vData[3]
            f=open(file+"-Milestones\\"+subject+" "+commiter+".txt","w");
            f.write(hashC)
            f.close()
            os.utime(file+"-Milestones\\"+subject+" "+commiter+".txt",(int(date),int(date)))
            print(file+"-Milestones\\"+subject+" "+commiter+".txt",(int(date),int(date)))


    except Exception as inst:
        print(type(inst))     # the exception instance
        print(inst.args)      # arguments stored in .args
        print (inst)           # __str__ allows args to printed directly


def revertToMilestone(directory,file):
    if "Milestones" not in file:
        print("this file is not an older Milestone")
        return
    try:
        f=open(file,"r")
        ver=f.readline()
        f.close()
        origFile=directory.replace("-Milestones","")
        origDirectory=os.path.dirname(os.path.realpath(origFile))
#        res=subprocess.check_output([baseScript,origDirectory,"nf","git add "+origFile])
        res=subprocess.check_output([baseScript,origDirectory,"nf","git checkout "+ver+" -- "+origFile])
        res=subprocess.check_output([baseScript,origDirectory,"nf","git commit -m \"revert to milestone: "+os.path.basename(file)+"\" "+origFile])

    except Exception as inst:
        print(type(inst))     # the exception instance
        print(inst.args)      # arguments stored in .args
        print (inst)           # __str__ allows args to printed directly


def main():
    option=sys.argv[1]
    file=sys.argv[2]
    directory=os.path.dirname(os.path.realpath(file))
    #print(option+" "+directory+" "+file+"\n")
    if(option=='1'):
        markMileStone(directory,file)
    if(option=='2'):
        showMilestone(directory,file)
    if(option=='3'):
        revertToMilestone(directory,file)

#    a=subprocess.check_output([baseScript,directory,file,"git status"])
#    print(a)
    input()

if __name__ == '__main__':
    main()