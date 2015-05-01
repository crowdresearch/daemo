/**
* HomeController
* @namespace crowdsource.home.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.home.controllers',['ui.bootstrap'])
    .controller('HomeController', HomeController);

  HomeController.$inject = ['$location', '$scope','$http', 'Authentication'];

  /**
  * @namespace HomeController
  */
  function HomeController($location, $scope,$http, Authentication) {
    var vm = this;
      if (Authentication.isAuthenticated())
      {
         /* $http.get("/static/templates/catalog/main.html").success(function(response){
              $scope.mycontent = response;
          });*/
          $location.path( "/main" );
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