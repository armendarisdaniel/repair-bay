from fastapi import FastAPI, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
import random
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
app = FastAPI()

# Tabla de sistemas dañados y sus códigos
system_codes = {
    "navigation": "NAV-01",
    "communications": "COM-02",
    "life_support": "LIFE-03",
    "engines": "ENG-04",
    "deflector_shield": "SHLD-05"
}

# Dependencia para obtener el sistema dañado
def get_damaged_system() -> str:
    # Simulamos que el sistema dañado es aleatorio
    print("get_damaged_system")
    print(1)
    return random.choice(list(system_codes.keys()))

# Ruta para obtener el estado del sistema dañado
@app.get("/status")
async def get_status(damaged_system: str = Depends(get_damaged_system)):
    # Crear el diccionario para el nuevo documento
    damaged_system_data = {
        "damaged_system": damaged_system,
        "timestamp": firestore.SERVER_TIMESTAMP  # Esto agrega la hora actual automáticamente
    }

    db.collection("damages").add(damaged_system_data)
    return {"damaged_system": damaged_system}

# Ruta para obtener la página HTML con el código del sistema averiado
@app.get("/repair-bay", response_class=HTMLResponse)
async def get_repair_bay():
    
    docs = db.collection("damages") \
         .order_by("timestamp", direction=firestore.Query.DESCENDING) \
         .limit(1) \
         .get()

    extracted_code = docs[0].to_dict()
    extracted_code = extracted_code["damaged_system"]

    if  extracted_code not in system_codes:
        return HTMLResponse(content="Sistema no válido.", status_code=status.HTTP_400_BAD_REQUEST)

    system_code = system_codes[extracted_code]

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Repair</title>
    </head>
    <body>
    <div class="anchor-point">{system_code}</div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Ruta para la tercera llamada, que retorna un código de estado HTTP 418
@app.get("/teapot")
async def teapot():
    return JSONResponse(
        content={"detail": "I'm a teapot"},
        status_code=418
    )


