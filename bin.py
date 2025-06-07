from fastapi import FastAPI
from pydantic import BaseModel
from estrategias.cripto1h import analizar_cripto1h
from estrategias.signalpro import analizar_signalpro
from estrategias.senal_automatica import analizar_senal_automatica
from estrategias.fxpro import analizar_fxpro
from estrategias.scalping_sniper import analizar_scalping_sniper

app = FastAPI()

class Entrada(BaseModel):
    activo: str
    intervalo: str
    estrategia: str

@app.post("/analizar")
async def analizar(info: Entrada):
    estrategia = info.estrategia.lower()

    if estrategia == "cripto1h":
        return await analizar_cripto1h(info)
    elif estrategia == "signalpro":
        return await analizar_signalpro(info)
    elif estrategia == "fxpro":
        return await analizar_fxpro(info)
    elif estrategia == "scalping":
        return await analizar_scalping_sniper(info)
    elif estrategia == "senal_automatica":
        return await analizar_senal_automatica(info)
    else:
        return {"analisis": f"❌ Estrategia '{info.estrategia}' no reconocida."}