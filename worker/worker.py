import logging
import socket
import time
import requests
import os
import json
from redis import Redis
from pygelf import GelfUdpHandler

# Lấy hostname container để log
hostname = socket.gethostname()
service = "worker"

# Cấu hình logger với mức INFO
log = logging.getLogger("worker")
log.setLevel(logging.INFO)

# Thiết lập thông số kết nối đến Logstash thông qua GELF
logstash_host = "logstash"
logstash_port = 12201

# Custom GELF handler: Định dạng log thành JSON với trường 'short_message' và 'full_message'
class CustomGelfUdpHandler(GelfUdpHandler):
    def make_gelf_dict(self, record):
        base = super().make_gelf_dict(record)
        try:
            # Nếu record.msg là chuỗi JSON, chuyển về dict
            if isinstance(record.msg, str):
                msg_dict = json.loads(record.msg)
            else:
                msg_dict = record.msg
            base['short_message'] = msg_dict.get("event", "log-event")
            base['full_message'] = json.dumps(msg_dict)
        except Exception:
            base['short_message'] = str(record.msg)
            base['full_message'] = str(record.msg)
        return base

# Thêm handler vào logger
gelf_handler = CustomGelfUdpHandler(
    host=logstash_host, 
    port=logstash_port, 
    include_full_message=True
)
log.addHandler(gelf_handler)

# Khởi tạo Redis client
redis = Redis(host=os.environ.get("REDIS_HOST", "redis"))

# Hàm gọi service RNG để lấy 32 byte ngẫu nhiên
def get_random_bytes():
    r = requests.get("http://rng/32")
    return r.content

# Hàm gọi service Hasher để chuyển đổi dữ liệu sang hash
def hash_bytes(data):
    text = data.hex()
    r = requests.post("http://hasher/", data={"data": text})
    return r.text

# Thực hiện một đơn vị công việc
def work_once():
    start_time = time.time()
    
    # Log bắt đầu xử lý work unit (nếu cần)
    log.debug(json.dumps({
        "event": "work_unit_start",
        "service": service,
        "hostname": hostname
    }))
    
    # Lấy dữ liệu ngẫu nhiên và tính hash
    random_bytes = get_random_bytes()
    hex_hash = hash_bytes(random_bytes)
    latency = round(time.time() - start_time, 4)
    
    # Nếu hash không bắt đầu bằng '0', thì không tìm thấy coin
    if not hex_hash.startswith('0'):
        log_data = {
            "event": "no_coin_found",
            "hex_hash": hex_hash,
            "latency_seconds": latency,
            "service": service,
            "hostname": hostname,
            "status": "failure"
        }
        log.info(json.dumps(log_data))
        return

    # Nếu tìm thấy coin
    log_data = {
        "event": "coin_found",
        "hex_hash": hex_hash,
        "short_hash": hex_hash[:8],
        "latency_seconds": latency,
        "service": service,
        "hostname": hostname,
        "status": "success"
    }
    log.info(json.dumps(log_data))
    
    # Lưu coin vào Redis
    created = redis.hset("wallet", hex_hash, random_bytes)
    if not created:
        log_data = {
            "event": "coin_duplicate",
            "hex_hash": hex_hash,
            "service": service,
            "hostname": hostname
        }
        log.info(json.dumps(log_data))
        
# Vòng lặp công việc, mỗi batch đếm số đơn vị đã xử lý
def work_loop(interval=1):
    deadline = time.time() + interval
    loops_done = 0
    while True:
        if time.time() >= deadline:
            log_data = {
                "event": "batch_complete",
                "units_done": loops_done,
                "service": service,
                "hostname": hostname
            }
            log.info(json.dumps(log_data))
            redis.incrby("hashes", loops_done)
            loops_done = 0
            deadline = time.time() + interval

        work_once()
        loops_done += 1

if __name__ == "__main__":
    while True:
        try:
            work_loop()
        except Exception:
            log.exception("Worker crashed, restarting", extra={
                "service": service,
                "hostname": hostname
            })
            time.sleep(10)
