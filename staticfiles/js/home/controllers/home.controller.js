/**
* HomeController
* @namespace crowdsource.home.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.home.controllers')
    .controller('HomeController', HomeController);

  HomeController.$inject = ['$location', '$scope', 'Authentication'];

  /**
  * @namespace HomeController
  */
  function HomeController($location, $scope, Authentication) {
    var vm = this;
  }
})();