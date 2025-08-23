# api/remove_friend.py
from flask import Flask, request, jsonify
import requests
from byte import Encrypt_ID, encrypt_api  # تأكد وجود byte.py بنفس المسار

app = Flask(__name__)

@app.route("/remove_friend", methods=["GET"])
def remove_friend():
    try:
        token = request.args.get("token")
        uid = request.args.get("uid")

        if not token or not uid:
            return jsonify({"error": "Missing token or uid"}), 400

        uid = int(uid)
        id_encrypted = Encrypt_ID(uid)
        data0 = "08c8b5cfea1810" + id_encrypted + "18012008"
        data = bytes.fromhex(encrypt_api(data0))

        url = "https://clientbp.ggblueshark.com/GetBackpack"
        headers = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)',
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'Authorization': f'Bearer {token}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB50',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.post(url, headers=headers, data=data, verify=False)

        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Friend removed or action completed!"})
        else:
            return jsonify({
                "status": "failed",
                "code": response.status_code,
                "response": response.text
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204

# هذه السطر مهم لتحويل Flask إلى Serverless Function على Vercel
from vercel_wsgi import handle_wsgi
def handler(request, context):
    return handle_wsgi(app, request, context)
  
