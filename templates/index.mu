<div ng-app="app" ng-controller="CommandCenter">
  <section ng-repeat="host in $storage.hosts">
    - {{host}}
  </section>
</div>
