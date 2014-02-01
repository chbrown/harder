<div ng-app="app" ng-controller="CommandCenter">
  <section ng-repeat="host in hosts">
    {{host}}
  </section>
</div>

<script>
// refresh every 10s
setTimeout(function() {
  window.location = window.location;
}, 10000);
</script>
