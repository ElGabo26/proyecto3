import os
from pathlib import Path
from typing import List, Literal


def openPath(rootPath:str)-> tuple[list,str,str]:
    dirs=os.listdir(rootPath)
    label=rootPath.split("/")[2]
    case=rootPath.split("/")[-1]
    return label, case, dirs


def getPaths(root):
    pathsCorrecto=[f"{root}/correcto/{x}" for  x in os.listdir(root+"/correcto")]
    pathsIncorrecto=[f"{root}/Incorrecto/{x}" for  x in os.listdir(root+"/Incorrecto")]
    pathsC=[]
    pathsCF=[]
    pathsI=[]
    pathsIF=[]
    
    for x  in  pathsCorrecto:
        rc=[f"{x}/{x1}"for x1 in os.listdir(x) ]
        pathsC.extend(rc)
    for x in pathsC:
        rcf=[f"{x}/{x1}" for x1 in os.listdir(x) ]
        pathsCF.extend(rcf)
    
    for x  in  pathsIncorrecto:
        rc=[f"{x}/{x1}"for x1 in os.listdir(x) ]
        pathsI.extend(rc)
    for x in pathsI:
        rcf=[f"{x}/{x1}" for x1 in os.listdir(x) ]
        pathsIF.extend(rcf)
    
        
    return pathsCF + pathsIF

if __name__ =="__main__":
    root=r"C:\Users\Gabo\Desktop\proyecto3\bencMark"
    result=getPaths(root)
    print(len(result[0]))
    print(len(result[1]))
    
    
    