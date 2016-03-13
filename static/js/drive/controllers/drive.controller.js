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

  DriveController.$inject = ['$window', '$location', '$scope', '$mdToast', 'Drive', '$filter', '$stateParams'];

  /**
  * @namespace DriveController
  */
  function DriveController($window, $location, $scope, $mdToast, Drive, $filter, $stateParams) {
      var self = this;
      self.addDriveAccount = addDriveAccount;
      finishAddAccount();
      function addDriveAccount() {
          Drive.addDriveAccount().then(
            function success(data, status) {
                $window.location.href = data[0].authorize_url;
            },
            function error(resp) {
              $mdToast.showSimple('Could not start adding drive account.');
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
                    $mdToast.showSimple('Could not finish adding drive account.');
                  }).finally(function () {

                  });
          }
      }
      
  }
})();