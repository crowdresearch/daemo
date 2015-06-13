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

	Requester.getRequesterTaskPortfolio().success(function(data) {
      $scope.requesterTaskPortfolio = data;

     
      $scope.getAcceptedRate= function (repetitions,totalSubmissions) {
      var accepted = parseInt(parseInt(repetitions)/parseInt(totalSubmissions) *100).toFixed(2);
            return accepted;

        };

	$scope.getRejectedRate= function (repetitions,totalSubmissions) {
      var rejected = 100-(parseInt(parseInt(repetitions)/parseInt(totalSubmissions) * 100).toFixed(2));
            return rejected;

        };

        $scope.range = new Array(5);
	$scope.convertToInt= function (value) {
            return parseInt(value);
        };
    });
  }
})();
