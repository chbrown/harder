/*jslint browser: true, devel: true */ /*globals _, p, angular */

var app = angular.module('app', ['ngStorage']);

app.controller('CommandCenter', function($scope, $localStorage, $http, $q) {
  // $scope.hosts = [];
  $scope.$storage = $localStorage.$default({
    hosts: []
  });
  p('CommandCenter init', $scope.$storage.hosts);

  var websocket = new WebSocket('ws://markov.ling.utexas.edu:3842/');
  websocket.addEventListener('message', function(ev) {
    p('ws.on("message") => ', ev, ev.data);
    $scope.$apply(function() {
      $scope.$storage.hosts.push(ev.data);
    });
  });
});

