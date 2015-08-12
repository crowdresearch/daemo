/**
* UserController
* @namespace crowdsource.worker.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.user.controllers')
    .controller('UserController', UserController);

  UserController.$inject = ['$location', '$scope',
   '$routeParams', '$mdToast', 'Authentication', 'User', 'Skill'];

  /**
  * @namespace UserController
  */
  function UserController($location, $scope,
    $routeParams, $mdToast, Authentication, User, Skill) {

    var vm = this;
    var userAccount = Authentication.getAuthenticatedAccount();
    if (!userAccount) {
      $location.path('/login');
      return;
    }
      User.getProfile(userAccount.username)
      .then(function(data) {
        $scope.user = data[0];
        // Make worker id specific
        $scope.user.workerId = $scope.user.id;


      });
  }
})();