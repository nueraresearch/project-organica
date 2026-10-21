'''inception_api.py
A minimal Flask server exposing Organica health metrics (via metrics.py) as JSON endpoints.
The Inception module or any external client can POST payloads to trigger actions
without stopping the daemon.
'''\n\nfrom flask import Flask, jsonify, request\nimport pathlib\nimport threading\nfrom metrics import snapshot_to_json\n\napp = Flask(__name__)\n\nSNAPSHOT_DIR = pathlib.Path(__file__).parent / "snapshots"
\n@app.route('/metrics', methods=['GET'])
def get_metrics():
    data = snapshot_to_json()
    return jsonify(data)
\n@app.route('/metrics/snapshot', methods=['POST'])
def create_snapshot():
    timestamp = pathlib.datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    path = SNAPSHOT_DIR / f'snapshot_{timestamp}.json'
    data = snapshot_to_json(path)
    return jsonify({'snapshot_path': str(path), 'status': 'created'})
\ndef run_server(host='127.0.0.1', port=8000):
    # Run Flask in a daemon thread so it does not block other tasks.
    threading.Thread(target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False), daemon=True).start()
\nif __name__ == '__main__':
    run_server()
