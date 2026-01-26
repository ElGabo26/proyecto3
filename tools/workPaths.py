import os
def openPath(rootPath:str)-> tuple[list,str,str]:
    dirs=os.listdir(rootPath)
    label=rootPath.split("/")[2]
    case=rootPath.split("/")[-1]
    return label, case, dirs