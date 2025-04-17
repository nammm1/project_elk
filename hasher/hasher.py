from flask import Flask, Response, request, jsonify
import os, socket, time, hashlib, logging, json
from pygelf import GelfUdpHandler

app = Flask(__name__)
app.debug = False

hostname = socket.gethostname()

# GELF → Logstash
logstash_host = 'logstash'
logstash_port = 12201

logging.getLogger('werkzeug').disabled = True
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Cấu hình GelfHandler với message template phù hợp
class CustomGelfUdpHandler(GelfUdpHandler):
    def make_gelf_dict(self, record):
        base = super().make_gelf_dict(record)
        # Ghi JSON chi tiết vào full_message để Logstash filter parse
        try:
            msg_dict = json.loads(record.msg)
            base['short_message'] = msg_dict.get("event", "log-event")
            base['full_message'] = json.dumps(msg_dict)
        except Exception:
            base['short_message'] = str(record.msg)
            base['full_message'] = str(record.msg)
        return base

logger.addHandler(CustomGelfUdpHandler(host=logstash_host, port=logstash_port))

@app.route('/', methods=['POST'])
def index():
    start_time = time.time()
    data = request.form.get('data')
    if data is None:
        latency = time.time() - start_time
        log_data = {
            "event": "POST request failed (no data)",
            "latency_seconds": round(latency, 4),
            "status": "failure",
            "hostname": hostname,
			"service":"hasher"
        }
        logger.warning(json.dumps(log_data))
        return Response("Missing 'data'", status=400)

    result = hashlib.md5(data.encode()).hexdigest()
    time.sleep(0.1)
    latency = time.time() - start_time
    log_data = {
        "event": "POST request processed",
        "data_received": data,
        "hashed_result": result,
        "latency_seconds": round(latency, 4),
        "hostname": hostname,
        "status": "success",
		"service":"hasher"
    }
    logger.info(json.dumps(log_data))
    return jsonify({"hashed_result": result, "latency_seconds": round(latency, 4)})

@app.route('/', methods=['GET'])
def disp():
    start_time = time.time()
    latency = time.time() - start_time
    log_data = {
        "event": "GET request processed",
        "latency_seconds": round(latency, 4),
        "hostname": hostname,
        "status": "success",
		"service":"hasher"
    }
    logger.info(json.dumps(log_data))
    return f"HASHER running on {hostname}\n"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=False, use_reloader=False)
