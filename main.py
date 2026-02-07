import re
import os
from time import time
from openai import OpenAI 
import pandas as pd
from tools.readDocumentsPath import get_file_content_from_path
from tools.makeContext import limpiar_respuesta_deepseek, build_prompt
from tools.workPaths import openPath, getPaths


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
models=["llama3.1:8b","llama3.2:3b","deepseek-r1:1.5b","deepseek-r1:7b"]

root ="./bencMark"
folders=getPaths(root)


trys=2

if __name__ == '__main__':
    final=[] 
    for i in range(trys):
        print(f"INTENTO {i+1}")
        r1=[]
        for MODELO_D  in models:
            
            try:
                print(f"MODELO {MODELO_D}")
                r=list(map(lambda x: getResponse(x,
                                            client,
                                            MODELO_D,
                                            0.1),
                    folders))
                resultD=pd.DataFrame(r)
                resultD['model']=MODELO_D
                resultD.to_csv(f"./{MODELO_D}_{i}.csv")
                
                
            except Exception as e:
                print("ERROR")
                print(e)
                resultD=None
            print(resultD.shape)
            r1.append(resultD)
        
                
        results=[x for x in results if not x]
        results=pd.concat(r1)
        results['try']=i
        final.append(results)
    
    final=pd.concat(final) 
    final.to_csv("./resultados.csv")
        
        
