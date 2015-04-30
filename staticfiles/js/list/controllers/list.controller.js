/**
* ListController
* @namespace crowdsource.list.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.list.controllers')
    .controller('ListController', HomeController);

  HomeController.$inject = ['$location', '$scope'];

  /**
  * @namespace HomeController
  */
  function HomeController($location, $scope,$http, Authentication) {


  }
})();