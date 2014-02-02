/*jslint browser: true, devel: true */ /*globals _, p, angular, Url */
var app = angular.module('app', ['ngStorage']);

app.controller('CommandCenter', function($scope, $localStorage, $http, $q) {
  $scope.hosts = {};
  $scope.monitor = [];

  $http.get('/hosts').then(function(res) {
      // res has .data, .status, .headers, and .config values
      // p('GET /hosts', res.data);
      res.data.forEach($scope.refresh);
    }, function(res) {
      p('GET /hosts error', res);
    });

  $scope.putTask = function(host, task) {
    $http({method: 'PUT', url: '/hosts/' + host + '/' + task}).then(function(res) {
      // p('PUT /hosts/:host/' + task, res.data);
    });
  };

  $scope.refresh = function(host) {
    $http.get('/hosts/' + host).then(function(res) {
      // p('GET /hosts/:host', res.data);
      // use _.extend to update the data
      $scope.hosts[host] = _.extend({}, $scope.hosts[host], res.data);
    });
  };

  // set up websockets
  var ws_url = Url.parse(window.location).merge({protocol: 'ws'});

  var action_websocket = new WebSocket(ws_url.merge({path: '/action'}));
  action_websocket.onmessage = function(ev) {
    // action messages consist of a host and a message arising from that host
    // the local server combines them for the benefit of sending them across websockets to this app
    // but in redis they are send across unique channels.
    // because the host is a given, they will all look like ":host=:action"
    var parts = ev.data.split('=');
    var host = parts[0];
    var action = parts[1];
    $scope.$apply(function() {
      $scope.hosts[host] = _.extend({}, $scope.hosts[host], {action: action});
      if (action == 'ready' || action == 'change') {
        // we only refresh when we know there are new going to be new variables
        $scope.refresh(host);
      }
    });
  };
  action_websocket.onclose = function(ev) {
    p('oh no, closing!', ev);
  };
  action_websocket.onerror = function(ev) {
    p('action websocket error:', ev);
  };

  var monitor_websocket = new WebSocket(ws_url.merge({path: '/monitor'}));
  monitor_websocket.addEventListener('message', function(ev) {
    $scope.$apply(function() {
      $scope.monitor.push(ev.data);
    });
  });
});
