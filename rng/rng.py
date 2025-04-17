from flask import Flask, Response, request
import os
import socket
import time
import logging
import json
from pygelf import GelfUdpHandler

app = Flask(__name__)

# Enable debugging if the DEBUG environment variable is set and starts with Y
app.debug = os.environ.get("DEBUG", "").lower().startswith('y')

hostname = socket.gethostname()
urandom = os.open("/dev/urandom", os.O_RDONLY)

# Logging setup
logstash_host = 'logstash'
logstash_port = 12201

logging.getLogger('werkzeug').disabled = True
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Custom GELF handler to match Logstash filter
class CustomGelfUdpHandler(GelfUdpHandler):
    def make_gelf_dict(self, record):
        base = super().make_gelf_dict(record)
        try:
            msg_dict = json.loads(record.msg)
            base['short_message'] = msg_dict.get("event", "log-event")
            base['full_message'] = json.dumps(msg_dict)
        except Exception:
            base['short_message'] = str(record.msg)
            base['full_message'] = str(record.msg)
        return base

logger.addHandler(CustomGelfUdpHandler(host=logstash_host, port=logstash_port))

@app.route("/")
def index():
    start_time = time.time()
    latency = time.time() - start_time
    log_data = {
        "event": "GET / (index) request",
        "latency_seconds": round(latency, 4),
        "hostname": hostname,
        "status": "success",
		"service":"rng"
    }
    logger.info(json.dumps(log_data))
    return f"RNG running on {hostname}\n"


@app.route("/<int:how_many_bytes>")
def rng(how_many_bytes):
    start_time = time.time()
    time.sleep(0.1)
    data = os.read(urandom, how_many_bytes)
    latency = time.time() - start_time
    log_data = {
        "event": "GET /<int:how_many_bytes> request",
        "bytes_requested": how_many_bytes,
        "latency_seconds": round(latency, 4),
        "hostname": hostname,
        "status": "success",
		"service":"rng"
    }
    logger.info(json.dumps(log_data))
    return Response(data, content_type="application/octet-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
