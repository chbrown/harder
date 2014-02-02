<div ng-app="app" ng-controller="CommandCenter">
  <section ng-repeat="(name, status) in hosts" class="host">
    <h2>{{name}}</h2>
    <table>
      <tr ng-repeat="(key, value) in status">
        <td>{{key}}</td><td>{{value}}</td>
      </tr>
    </table>
    <button ng-click="putTask(name, 'eject')">Eject</button>
    <button ng-click="putTask(name, 'reload')">Reload</button>
    <button ng-click="putTask(name, 'copy')">Copy</button>
  </section>

  <section class="monitor">
    <h4>Monitor</h4>
    <div ng-repeat="line in monitor track by $index" class="log">
      <span style="float: right">{{$index}}</span>
      <code>{{line}}</code>
    </div>
  </section>
</div>
