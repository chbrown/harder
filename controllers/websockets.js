/*jslint node: true */
var ws = require('ws');
var redis = require('redis');
var logger = require('loge');
var ns = require('../lib').ns;

var toLocalISOString = function(date) {
  return new Date(date.getTime() + date.getTimezoneOffset()*60*1000).toISOString().replace(/\..+/, '');
};

var action_server = new ws.Server({noServer: true});
var monitor_server = new ws.Server({noServer: true});

var helo = function(client) {
  logger.debug('websocket connection established (url: %s)', client.upgradeReq.url);
  // client.send('');
};

module.exports = function(req, socket, upgradeHead) {
  if (req.url == '/monitor') {
    logger.debug('attaching websocket connection to monitor_server');
    monitor_server.handleUpgrade(req, socket, upgradeHead, helo);
  }
  else {
    logger.debug('attaching websocket connection to action_server');
    action_server.handleUpgrade(req, socket, upgradeHead, helo);
  }
};

(function() {
  // subscribe to 'harder:*:action' pattern
  var client = redis.createClient();
  client.on('pmessage', function(pattern, channel, message) {
    logger.info('action received:', pattern, channel, message);
    var host = channel.split(':')[1];
    action_server.clients.forEach(function(client) {
      // {host: host, action: message}
      // nvm, send them across the websocket wire as a simple string like ":host=:action"
      client.send(host + '=' + message);
    });
  });
  client.psubscribe(ns('*', 'action'), function(err, pattern) {
    logger.info('psubscribe result = %s', pattern);
  });
})();

(function monitor_loop() {
  var client = redis.createClient();
  client.monitor(function(err, res) {
    if (err) return logger.error('redis.monitor error:', err);

    logger.info('Entering monitoring mode.');
  });
  client.on('monitor', function(time, args) {
    var date = new Date(time*1000);
    var local_datetime_str = toLocalISOString(date);
    // util.inspect(args)
    var message = local_datetime_str + ' $ ' + args.join(' ');
    logger.debug('monitor:', message);
    monitor_server.clients.forEach(function(client) {
      client.send(message);
    });
  });
})();


// R.any(/\/ws\/(\w+)/, function(req, res, m) {
//   var path = m[1];
// });

// var websocket_monitor_server = new ws.Server({port: 3842, path: 'monitor'});
// websocket_monitor_server.on('connection', function(ws) {
  // logger.debug('monitor connection established.',);
// });

  // port: 3842
// }).on('connection', function(ws) {

  // ws.on('message', function(message) {
  //     console.log('received: %s', message);
  // });
  // setTimeout(function() {
  //   ws.send('delayed welcome: hey!');
  // }, 2000);
// }).on('error', function(err) {
//   logger.error('ws error', err);
// });

// websocket.on('open', function() {
//     websocket.send('something');
// });
// websocket.on('message', function(data, flags) {
//   // flags.binary will be set if a binary data is received
//   // flags.masked will be set if the data was masked
// });
