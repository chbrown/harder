/*jslint node: true */
exports.ns = function() {
  return Array.prototype.concat.apply(['harder'], arguments).join(':');
};
