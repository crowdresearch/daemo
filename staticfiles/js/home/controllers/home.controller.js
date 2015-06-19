/**
* HomeController
* @namespace crowdsource.home.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.home.controllers')
    .controller('HomeController', HomeController);

  HomeController.$inject = ['$location', '$scope', 'Authentication', '$mdSidenav', '$mdUtil'];

  /**
  * @namespace HomeController
  */
  function HomeController($location, $scope, Authentication, $mdSidenav, $mdUtil) {
    var self = this;
    self.sideNavToggler = sideNavToggler;

      function sideNavToggler(navID) {
      var debounceFn =  $mdUtil.debounce(function(){
        $mdSidenav(navID)
          .toggle()
          .then(function () {
          });
        },300);
        return debounceFn;
      }
  }
})();