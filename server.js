/*jslint node: true */
var http = require('http-enhanced');
var path = require('path');

var logger = require('loge');

var amulet = require('amulet');
amulet.set({open: '<%', close: '%>', root: path.join(__dirname, 'templates')});

var optimist = require('optimist')
  .describe({
    hostname: 'hostname to listen on',
    port: 'port to listen on',

    help: 'print this help message',
    verbose: 'print extra output',
    version: 'print version',
  })
  .boolean(['help', 'verbose', 'version'])
  .alias({verbose: 'v'})
  .default({
    hostname: '127.0.0.1',
    port: 3841,
  });

var argv = optimist.argv;
logger.level = argv.verbose ? 'debug' : 'info';

if (argv.help) {
  optimist.showHelp();
}
else if (argv.version) {
  console.log(require('./package').version);
}
else {
  var root_controller = require('./controllers');

  http.createServer(function(req, res) {
    logger.debug('%s %s', req.method, req.url);
    root_controller(req, res);
  }).listen(argv.port, argv.hostname, function() {
    logger.info('listening on http://%s:%d', argv.hostname, argv.port);
  });
}
