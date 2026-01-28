import re
import os
from time import time
from openai import OpenAI 
import pandas as pd
from tools.readDocumentsPath import get_file_content_from_path
from tools.makeContext import limpiar_respuesta_deepseek, build_prompt
from tools.workPaths import openPath

def getResponse(rootPath:str,client,modelName,temperature:float):
    resultado={"model":modelName,"temperature":temperature,
               "context":"","prompt":"","answer":""}
    archivos=openPath(rootPath)
    contexto_documentos = f"DE UN  TOTAL DE:{len(archivos[-1])} DOCUEMTOS CON LA SIGUIENTE INFORMACION\n"
    
    for archivo in archivos[-1]:
        contexto_documentos +=f"DOCUMENTO DE NOMBRE:{archivo}\nCONTENIDO:\n"
        contexto_documentos += get_file_content_from_path(f"{rootPath}/{archivo}")
        contexto_documentos += "\n"
        
    system_instruction = build_prompt(contexto_documentos)
    resultado['context']=system_instruction
    resultado['prompt']=contexto_documentos
    t0=time()
    try:
        
        response = client.chat.completions.create(
        model=modelName,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": contexto_documentos}
        ],
        temperature=temperature,
    )
        resultado['answer'] = response.choices[0].message.content
    
    except Exception as e:
        resultado["answer"]= f"Error en el servidor local: {str(e)}"
    t1=time()
    resultado['time']=t1-t0
    resultado['caso']=rootPath
    return resultado


# --- CONFIGURACIÓN LOCAL (OLLAMA) ---
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
# MODELOS
MODELO_D = "deepseek-r1:7b"
MODELO_L='llama3.1'


correcto="./benchMark/correcto"
incorrecto="./benchMark/Incorrecto"

correctoFiles=os.listdir(correcto)
correctoFiles=[f"{correcto}/{x}" for x in correctoFiles]

incorrectoFiles=os.listdir(incorrecto)
incorrectoFiles=[f"{incorrecto}/{x}" for x in incorrectoFiles]
paths=correctoFiles+incorrectoFiles

trys=5

if __name__ == '__main__':
    print(paths)
    final=[] 
    for i in range(trys):
        print(f"INTENTO {i+1}")
        try:
            print(f"MODELO {MODELO_D}")
            r=list(map(lambda x: getResponse(x,
                                         client,
                                         MODELO_D,
                                         0.1),
                   paths))
            resultD=pd.DataFrame(r)
            resultD['model']=MODELO_D
            
        except Exception as e:
            print("ERROR")
            print(e)
            resultD=pd.DataFrame()
        try:
            print(f"MODELO {MODELO_L}")
            r1=list(map(lambda x: getResponse(x,
                                         client,
                                         MODELO_L,
                                         0.1),
                   paths))
            resultL=pd.DataFrame(r)
            resultL['model']=MODELO_L
            
        except Exception as e:
            print("ERROR")
            print(e)
            resultL=pd.DataFrame()
            
        results=pd.concat([resultD,resultL])
        results['try']=i
        final.append(results)
    
    final=pd.concat(final)
    final.to_csv("./resultados.csv")
        
        
