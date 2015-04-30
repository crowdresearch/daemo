/**
* HomeController
* @namespace crowdsource.home.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.home.controllers')
    .controller('HomeController', HomeController);

  HomeController.$inject = ['$location', '$scope','$http', 'Authentication'];

  /**
  * @namespace HomeController
  */
  function HomeController($location, $scope,$http, Authentication) {
    var vm = this;
      if (Authentication.isAuthenticated())
      {
          $http.get("/home").success(function(response){
              $scope.mycontent = response;
          });
      }
      else
      {
          $http.get("/static/templates/intro.html").success(function(response)
          {
              $scope.mycontent =response;


          });

      }
    $scope.account = Authentication.getAuthenticatedAccount();

  }
})();