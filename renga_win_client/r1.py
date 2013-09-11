import os
import sys
import subprocess
import shutil

base="C:\\Users\AlmondNET\\AppData\Local\\GitHub\\PortableGit_015aa71ef18c047ce8509ffb2f9e4bb0e3e73f13\\"
baseScript="C:\\Users\AlmondNET\\AppData\Local\\GitHub\\PortableGit_015aa71ef18c047ce8509ffb2f9e4bb0e3e73f13\\r1.bat"

def checkAndCreateRepo(directory):
        #check if repo exists
    try:
        res=subprocess.check_output([baseScript,directory,"git status"])
        print(res)
    except:
        #no repo , need to create one
        res=subprocess.check_output([baseScript,directory,"git init"])
        print(res)

def markMileStone(directory,file):
    directory=escapeStringForBatch(directory)
    file=escapeStringForBatch(file)
    try:
        checkAndCreateRepo(directory)
        res=subprocess.check_output([baseScript,directory,"git add "+file])
        print(res)
        print("Enter Commit note")
        commitNote=input()
        commitNote=escapeStringForBatch(commitNote)
        res=subprocess.check_output([baseScript,directory,"git commit -m "+commitNote+" "+file])
        print(res)
    except Exception as inst:
        a=1
        print(type(inst))     # the exception instance
        print(inst.args)      # arguments stored in .args
        print (inst)           # __str__ allows args to printed directly


def showMilestone(directory,file):
    try:
        try:
            res=subprocess.check_output([baseScript,escapeStringForBatch(directory),"git status"])
        #print(res)
        except:
            #no repo , exit
            print("no repo was found for this file ")
            return


        res=subprocess.check_output([baseScript,escapeStringForBatch(directory),"git log --reverse --format=%H,%an,%at,%s "+escapeStringForBatch(file)])
        vA=res.decode("utf-8").rstrip().split("\n")

        if not (os.path.isdir(file+"-Milestones")):
            os.makedirs(file+"-Milestones")
        else:
            shutil.rmtree(file+"-Milestones")
            os.makedirs(file+"-Milestones")

        for version in vA:
            vData=version.split(",")
            hashC=vData[0]
            commiter=vData[1]
            date=vData[2]
            subject=vData[3]
            newFileName=subject+" Commiter-"+commiter+".txt"
            res=subprocess.check_output([baseScript,escapeStringForBatch(file+"-Milestones"),"git --git-dir="+escapeStringForBatch(directory)+"\.git"+" checkout "+hashC+" "+escapeStringForBatch(os.path.basename(file))])
            print(res)
            res=subprocess.check_output([baseScript,escapeStringForBatch(file+"-Milestones"),"rename "+escapeStringForBatch(os.path.basename(file))+" "+escapeStringForBatch(newFileName)])
            print(res)
            f=open(directory+"\.git\map.txt","a");
            f.write(hashC+"\t"+newFileName+"\n")
            f.close()
            os.utime(file+"-Milestones\\"+newFileName,(int(date),int(date)))
            print(file+"-Milestones\\"+newFileName,(int(date),int(date)))


#fake files with the commit note at thier name
#            f=open(file+"-Milestones\\"+subject+" Commiter-"+commiter+".txt","w");
#            f.write(hashC)
#            f.close()
#            os.utime(file+"-Milestones\\"+subject+" Commiter-"+commiter+".txt",(int(date),int(date)))
#            print(file+"-Milestones\\"+subject+" Commiter-"+commiter+".txt",(int(date),int(date)))


    except Exception as inst:
        print(type(inst))     # the exception instance
        print(inst.args)      # arguments stored in .args
        print (inst)           # __str__ allows args to printed directly


def revertToMilestone(directory,file):
    if "Milestones" not in file:
        print("this file is not an older Milestone")
        return
    try:
        origFile=directory.replace("-Milestones","")
        origDirectory=os.path.dirname(os.path.realpath(origFile))
        mapFile=open(origDirectory+"\.git\map.txt","r")
        verMap={}
        for line in mapFile:
            if not line.strip()=='':
                ver=line.split("\t")[0].strip()
                fileName=line.split("\t")[1].strip()
                verMap[fileName]=ver
        mapFile.close()
        if not os.path.basename(file) in verMap:
            print("canno revert to this file "+ os.path.basename(file) +" has no version of it")
            return
        ver=verMap[os.path.basename(file)]
#        res=subprocess.check_output([baseScript,origDirectory,"nf","git add "+origFile])
        res=subprocess.check_output([baseScript,escapeStringForBatch(origDirectory),"git checkout "+ver+" -- "+escapeStringForBatch(origFile)])
        res=subprocess.check_output([baseScript,origDirectory,"git commit -m "+escapeStringForBatch("revert to milestone "+os.path.basename(file))+" "+escapeStringForBatch(origFile)])
        print(res)

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

def escapeStringForBatch(string):
    string="fakeQ"+string+"fakeQ"
    string=string.replace(" ","AAAA")
    return string

if __name__ == '__main__':
    main()