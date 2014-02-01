/*jslint node: true */
var request = require('request');
var amulet = require('amulet');
var Router = require('regex-router');
var http = require('http-enhanced');
var ws = require('ws');

var redis = require('redis');

var amulet = require('amulet');
var Router = require('regex-router');

var logger = require('loge');

var websocket_server = new ws.Server({port: 3842});
websocket_server.on('connection', function(ws) {
  logger.debug('ws connection established.');
  // ws.on('message', function(message) {
  //     console.log('received: %s', message);
  // });
  // setTimeout(function() {
  //   ws.send('delayed welcome: hey!');
  // }, 2000);
});

(function change_loop() {
  var client = redis.createClient();
  client.brpop('harder:change', 0, function(err, result) {
    if (err) logger.error('client brpop error:', err);
    var clients = websocket_server.clients;

    var key = result[0];
    var value = result[1];
    logger.debug('redis change: %s << %s; informing %d clients', key, value, clients.length);
    clients.forEach(function(client) {
      client.send(value + ' changed');
    });

    setImmediate(change_loop);
  });
})();
// websocket.on('open', function() {
//     websocket.send('something');
// });
// websocket.on('message', function(data, flags) {
//   // flags.binary will be set if a binary data is received
//   // flags.masked will be set if the data was masked
// });

var R = new Router(function(req, res) {
  res.die(404, 'No resource at: ' + req.url);
});

R.any(/^\/(static|favicon)/, require('./static'));

/** GET /
Show main page */
R.get('/', function(req, res) {
  var ctx = {};
  amulet.stream(['layout.mu', 'index.mu'], ctx).pipe(res);
});



R.get(/\/hosts\/(\w+).json/, function(req, res, m) {
  var client = redis.createClient();
  client.hgetall(m[1], function(err, hash) {
    if (err) return res.die('Redis error: ' + err.toString());

    res.json(hash);
  });
});

module.exports = R.route.bind(R);
