/**
* RequesterProfileController
* @namespace crowdsource.requester.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.requester.controllers')
    .controller('RequesterProfileController', RequesterProfileController);

  RequesterProfileController.$inject = ['$location', '$scope', 'Authentication','Requester'];

  /**
  * @namespace RequesterProfileController
  */
  function RequesterProfileController($location, $scope, Authentication, Requester) {
    var vm = this;

    Requester.getRequesterPrivateProfile().success(function(data) {
      $scope.requesterProfile = data;
    });
  }
})();