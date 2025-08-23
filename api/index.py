# api/remove_friend.py
from flask import Flask, request, jsonify
import requests
from byte import Encrypt_ID, encrypt_api
from concurrent.futures import ThreadPoolExecutor
import threading

app = Flask(__name__)
lock = threading.Lock()

def remove_friend_request(token, uid):
    try:
        uid_encrypted = Encrypt_ID(uid)
        data0 = "08c8b5cfea1810" + uid_encrypted + "18012008"
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
        resp = requests.post(url, headers=headers, data=data, verify=False)
        return {"token": token[:20]+"...", "status": resp.status_code, "text": resp.text[:100]}
    except Exception as e:
        return {"token": token[:20]+"...", "status": "error", "text": str(e)}

@app.route("/remove_friend", methods=["GET"])
def remove_friend():
    token = request.args.get("token")
    uid = request.args.get("uid")

    if not token or not uid:
        return jsonify({"error": "Missing token or uid"}), 400

    try:
        uid = int(uid)
    except ValueError:
        return jsonify({"error": "UID must be an integer"}), 400

    results = []

    # هنا نعمل 50 نافذة متوازية لكل Function
    def worker():
        res = remove_friend_request(token, uid)
        with lock:
            results.append(res)

    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(worker) for _ in range(50)]
        for future in futures:
            future.result()

    return jsonify({
        "player_uid": uid,
        "requests_sent": len(results),
        "results": results
    })

@app.route('/favicon.ico')
def favicon():
    return '', 204

# تحويل Flask إلى Serverless Function على Vercel
from vercel_wsgi import handle_wsgi
def handler(request, context):
    return handle_wsgi(app, request, context)

