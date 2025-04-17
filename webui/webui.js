var express = require('express');
var app = express();
var redis = require('redis');
var os = require('os');

var hostname = os.hostname();
var service = "webui";

// Hàm log tùy chỉnh xuất JSON với các field bổ sung
function logJSON(event, data) {
  data = data || {};
  data.event = event;
  data.service = service;
  data.hostname = hostname;
  data.timestamp = new Date().toISOString();
  console.log(JSON.stringify(data));
}

// Khởi tạo Redis client
var client = redis.createClient({ url: 'redis://redis:6379' });
client.on("error", function (err) {
  logJSON("redis_error", { error: err.message });
});

app.get('/', function (req, res) {
  res.redirect('/index.html');
});

app.get('/json', function (req, res) {
  client.hlen('wallet', function (err, coins) {
    if (err) {
      logJSON("redis_error", { error: err.message });
      res.status(500).json({ error: 'Redis error' });
      return;
    }
    client.get('hashes', function (err, hashes) {
      if (err) {
        logJSON("redis_error", { error: err.message });
        res.status(500).json({ error: 'Redis error' });
        return;
      }
      var now = Date.now() / 1000;
      var response = {
        coins: coins,
        hashes: hashes,
        now: now
      };
      logJSON("request_json", { response: response });
      res.json(response);
    });
  });
});

app.use(express.static('files'));

var PORT = 80;
var server = app.listen(PORT, function (err) {
  if (err) {
    logJSON("startup_error", { error: err.message });
  } else {
    logJSON("startup", { message: "WEBUI running on PORT " + PORT });
  }
});