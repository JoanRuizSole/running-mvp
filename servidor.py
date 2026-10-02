from flask import Flask, request, jsonify
from pymongo import MongoClient
import urllib.parse
import certifi  # <-- AFEGEIX AQUESTA LÍNIA A DALT

app = Flask(__name__)

usuari = urllib.parse.quote_plus("joanruizsole")
contrasenya = urllib.parse.quote_plus("Quintanes@15")
url_cluster = "cluster0.yud1xad.mongodb.net"

MONGO_URI = f"mongodb+srv://{usuari}:{contrasenya}@{url_cluster}/?retryWrites=true&w=majority"

# <-- AFEGEIX 'tlsCAFile=certifi.where()' A DINS DELS PARÈNTESIS
cliente = MongoClient(MONGO_URI, tlsCAFile=certifi.where()) 

db = cliente["de0a42k"]
coleccion = db["corredores"]

@app.route('/actualitzar_km', methods=['POST'])
def actualitzar_zapatilla():
    datos = request.json
    print("DADES REBUDES:", datos)
    id_zap = datos.get('id_zapatilla')
    km_nous = datos.get('km_recorreguts')
    
    # Consulta NoSQL nativa
    resultado = coleccion.update_one(
        {"_id": "atleta_principal", "zapatillas_activas.id_zapatilla": id_zap},
        {"$inc": {"zapatillas_activas.$.km_actuales": km_nous}}
    )
    
    if resultado.modified_count > 0:
        return jsonify({"estat": "èxit", "missatge": f"S'han sumat {km_nous} km correctament."})
    else:
        return jsonify({"estat": "error", "missatge": "No s'ha trobat la sabatilla."}), 404

if __name__ == '__main__':
    print("El servidor del MVP està en marxa al port 5000...")
    print("Esperant rebre els quilòmetres des del rellotge!")
    app.run(port=5000)