/*jslint browser: true, devel: true */ /*globals _, p, angular, Url */

var app = angular.module('app', ['ngStorage']);

app.controller('CommandCenter', function($scope, $localStorage, $http, $q) {
  $scope.hosts = {};
  $scope.monitor = [];

  // $scope.$storage = $localStorage.$default({
  //   hosts: []
  // });

  // p('CommandCenter init', $scope.$storage.hosts);
  $http.get('/hosts').then(function(res) {
      // res has .data, .status, .headers, and .config values
      p('GET /hosts', res.data);
      res.data.forEach($scope.refresh);
    }, function(res) {
      p('GET /hosts error', res);
    });

  $scope.putTask = function(host, task) {
    // p('PUT /hosts/:host/', res.data);
    $http({method: 'PUT', url: '/hosts/' + host + '/' + task}).then(function(res) {
      p('PUT /hosts/:host/' + task, res.data);
      // $scope.hosts[host] = res.data;
    });
  };

  $scope.refresh = function(host) {
    $http.get('/hosts/' + host).then(function(res) {
      p('GET /hosts/:host', res.data);
      // use _.extend to update the data
      $scope.hosts[host] = _.extend({}, $scope.hosts[host], res.data);
    });
  };

  // set up websockets
  var ws_url = Url.parse(window.location).merge({protocol: 'ws'});

  var action_websocket = new WebSocket(ws_url.merge({path: '/action'}));
  action_websocket.addEventListener('message', function(ev) {
    // action messages consist of ...
    p('action_websocket :: message =', ev.data);
    var parts = ev.data.split('=');
    var host = parts[0];
    var action = parts[1];
    $scope.$apply(function() {
      $scope.hosts[host].action = action;
      if (action == 'ready') {
        // we only refresh when there are new going to be new variables
        $scope.refresh(host);
      }
    });
  });

  var monitor_websocket = new WebSocket(ws_url.merge({path: '/monitor'}));
  monitor_websocket.addEventListener('message', function(ev) {
    // p('monitor_websocket :: message =', ev);
    $scope.$apply(function() {
      $scope.monitor.push(ev.data);
    });
  });

});

// new Url({protocol: 'ws'});
//
// var websocket = new WebSocket(url);
// websocket.addEventListener('message', function(ev) {
//   p('websocket:"message": ', ev, ev.data);
//   // $scope.$apply(function() {
//   //   $scope.$storage.hosts.push(ev.data);
//   // });
// });
