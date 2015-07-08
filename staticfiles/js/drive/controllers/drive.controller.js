/**
* DriveController
* @namespace crowdsource.drive.controllers
 * @author dmorina
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.drive.controllers')
    .controller('DriveController', DriveController);

  DriveController.$inject = ['$window', '$location', '$scope', 'Drive', '$filter', '$routeParams'];

  /**
  * @namespace DriveController
  */
  function DriveController($window, $location, $scope, Drive, $filter, $routeParams) {
      var self = this;
      self.addDriveAccount = addDriveAccount;
      finishAddAccount();
      function addDriveAccount() {
          Drive.addDriveAccount().then(
            function success(data, status) {
                $window.location.href = data[0].authorize_url;
            },
            function error(resp) {

          }).finally(function () {

          });
      }

      function finishAddAccount(){
          if( $location.search().code ) {
              Drive.finishAddDriveAccount($location.search().code).then(
                  function success(data, status) {
                      //$window.location.href = data[0].authorize_url;
                      console.log('Account added successfully');
                  },
                  function error(resp) {

                  }).finally(function () {

                  });
          }
      }

  }
})();