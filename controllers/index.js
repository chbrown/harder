/*jslint node: true */
var request = require('request');
var amulet = require('amulet');
var Router = require('regex-router');
var http = require('http-enhanced');

var amulet = require('amulet');
var Router = require('regex-router');

var logger = require('loge');

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

module.exports = R.route.bind(R);
