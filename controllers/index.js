/*jslint node: true */
var _ = require('underscore');
var amulet = require('amulet');
var async = require('async');
var http = require('http-enhanced');
var logger = require('loge');
var redis = require('redis');
// var request = require('request');
var Router = require('regex-router');

var ns = require('../lib').ns;

var R = new Router(function(req, res) {
  res.die(404, 'No resource at: ' + req.url);
});

var die = function(res, err) {
  logger.error('500 ERR:', err);
  return res.die('Server Error: ' + err.toString());
};

R.any(/^\/(static|favicon)/, require('./static'));

/** GET /
Show main page */
R.get('/', function(req, res) {
  amulet.stream(['layout.mu', 'index.mu'], {}).pipe(res);
});

/** GET /hosts
Get a list of the current hosts, using "KEYS harder:*" */
R.get(/^\/hosts$/, function(req, res, m) {
  var client = redis.createClient();
  // var key = ns(m[1]);
  client.keys(ns('*'), function(err, keys) {
    if (err) return die(res, err);

    var all_hosts = keys.map(function(key) {
      return key.split(':')[1];
    });

    var hosts = _.uniq(all_hosts);

    res.json(hosts);
  });
});


/** GET /hosts/:host
Return current hash representing state of host */
R.get(/^\/hosts\/(.+)$/, function(req, res, m) {
  var client = redis.createClient();
  var host = m[1];
  client.keys(ns(host, '*'), function(err, keys) {
    if (err) return die(res, err);

    client.mget(keys, function(err, values) {
      if (err) return die(res, err);

      var suffixes = keys.map(function(key) {
        return key.split(':')[2];
      });

      res.json(_.object(_.zip(suffixes, values)));
    });
  });
});

/** PUT /hosts/:host/tasks/:task
Add task to host's task queue
*/
R.put(/^\/hosts\/(.+?)\/(\w+)$/, function(req, res, m) {
  var client = redis.createClient();
  var host = m[1];
  var task = m[2];
  client.publish(ns(host, 'task'), task, function(err, result) {
    if (err) return res.die('Redis error: ' + err.toString());

    res.json(result);
  });
});

module.exports = R.route.bind(R);
