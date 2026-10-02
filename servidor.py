from flask import Flask, request, jsonify
from pymongo import MongoClient
import urllib.parse
import certifi

app = Flask(__name__)

# Connexió a la teva base de dades amb certificat segur
usuari = urllib.parse.quote_plus("joanruizsole")
contrasenya = urllib.parse.quote_plus("Quintanes@15")
url_cluster = "cluster0.yud1xad.mongodb.net"
MONGO_URI = f"mongodb+srv://{usuari}:{contrasenya}@{url_cluster}/?retryWrites=true&w=majority"

cliente = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = cliente["de0a42k"]
coleccion = db["corredores"]

# 1. Pàgina Principal amb la Taula Visual de les teves Hoka
@app.route('/', methods=['GET'])
def garatge_visual():
    try:
        atleta = coleccion.find_one({"_id": "atleta_principal"})
        zapatillas = atleta.get("zapatillas_activas", []) if atleta else []
        
        html = """
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Garatge Hoka - Odòmetre 42k</title>
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; color: #333; padding: 20px; max-width: 600px; margin: auto; }
                    h1 { text-align: center; color: #2c3e50; }
                    table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 20px; }
                    th, td { padding: 15px; text-align: left; border-bottom: 1px solid #dee2e6; }
                    th { background-color: #34495e; color: white; }
                    tr:hover { background-color: #f1f2f6; }
                    .km-actual { font-weight: bold; color: #27ae60; font-size: 1.1em; }
                    .footer { text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 0.9em; }
                </style>
            </head>
            <body>
                <h1>👟 El meu Garatge Hoka</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Km Actuals</th>
                            <th>Km Màxims</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        for zap in zapatillas:
            html += f"""
                        <tr>
                            <td><b>{zap.get('marca')} {zap.get('modelo')}</b></td>
                            <td class="km-actual">{zap.get('km_actuales')} km</td>
                            <td>{zap.get('km_maximos')} km</td>
                        </tr>
            """
        html += """
                    </tbody>
                </table>
                <div class="footer">Actualitzat automàticament des del Garmin & MongoDB</div>
            </body>
        </html>
        """
        return html
    except Exception as e:
        return f"Error carregant la base de dades: {str(e)}"

# 2. Ruta per rebre les dades des del teu Garmin
@app.route('/actualitzar_km', methods=['POST'])
def actualitzar_km():
    try:
        dades = request.get_json()
        id_zap = dades.get('id_zapatilla')
        km_nous = float(dades.get('km_recorreguts'))
        
        coleccion.update_one(
            {"_id": "atleta_principal", "zapatillas_activas.id_zapatilla": id_zap},
            {"$inc": {"zapatillas_activas.$.km_actuales": km_nous}}
        )
        return jsonify({"estat": "èxit", "missatge": f"S'han sumat {km_nous} km."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
