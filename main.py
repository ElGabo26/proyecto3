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
    contexto_documentos = f"DE UN  TOTAL DE:{len(archivos)} DOCUMENTOS CON LA SIGUIENTE INFORMACION"
    
    for archivo in archivos[-1]:
        contexto_documentos +=f"DOCUMENTO DE NOMBRE:{archivo}\nCONTENIDO:\n"
        contexto_documentos += get_file_content_from_path(f"{rootPath}/{archivo}")
        
    system_instruction = build_prompt(contexto_documentos)
    resultado['context']=system_instruction
    resultado['prompt']=contexto_documentos
    
    try:
        print(modelName)
        t0=time()    
        response = client.chat.completions.create(
        model=modelName,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": contexto_documentos}
        ],
        temperature=temperature,
    )
        resultado['answer'] = response.choices[0].message.content
        t1=time()
    except Exception as e:
        t1, t0=0,0
        resultado["answer"]= f"Error en el servidor local: {str(e)}"
    
    resultado['time']=t1-t0
    resultado['caso']=rootPath
    return resultado


# --- CONFIGURACIÓN LOCAL (OLLAMA) ---
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
# MODELOS
models=["llama3.1:8b","llama3.2:3b","deepseek-r1:1.5b","deepseek-r1:1.7b"],


correcto="./benchMark/correcto"
incorrecto="./benchMark/Incorrecto"

correctoFiles=os.listdir(correcto)
correctoFiles=[f"{correcto}/{x}" for x in correctoFiles]

incorrectoFiles=os.listdir(incorrecto)
incorrectoFiles=[f"{incorrecto}/{x}" for x in incorrectoFiles]

paths=correctoFiles+incorrectoFiles

trys=5

if __name__ == '__main__':
    final=[] 
    for i in range(trys):
        print(f"INTENTO {i+1}")
        for MODELO_D  in models:
            r=[]
            print(MODELO_D)
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
            r.append(resultD)
                
        results=pd.concat(r)
        results['try']=i
        final.append(results)
    
    final=pd.concat(final) 
    final.to_csv("./resultados.csv")
        
        
