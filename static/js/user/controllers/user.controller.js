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
        '$window', '$mdToast', '$mdDialog', 'Authentication', 'User', 'Payment'];

    /**
     * @namespace UserController
     */
    function UserController($location, $scope,
                            $window, $mdToast, $mdDialog, Authentication, User, Payment) {

        var vm = this;
        vm.paypal_payment = paypal_payment;

        var userAccount = Authentication.getAuthenticatedAccount();
        if (!userAccount) {
            $location.path('/login');
            return;
        }

        User.getProfile(userAccount.username)
            .then(function (data) {
                var user = data[0];
                user.first_name = userAccount.first_name;
                user.last_name = userAccount.last_name;

                if (user.hasOwnProperty('financial_accounts') && user.financial_accounts) {
                    user.financial_accounts = _.filter(user.financial_accounts.map(function (account) {
                        var mapping = {
                            'general': 'general',
                            'requester': 'Deposits',
                            'worker': 'Earnings'
                        };

                        account.type = mapping[account.type];
                        return account;
                    }), function (account) {
                        return account.type != 'general';
                    });
                }

                vm.user = user;
                // Make worker id specific
                vm.user.workerId = user.id;
            });

        function paypal_payment($event){
            var parent = angular.element(document.body);

            $mdDialog.show({
                clickOutsideToClose: false,
                scope: $scope,
                preserveScope: true,
                parent: parent,
                targetEvent: $event,
                templateUrl: '/static/templates/payment/payment.html',
                locals: {
                    project: vm.user
                },
                controller: DialogController
            });

            function DialogController($scope, $mdDialog) {

                $scope.payment_in_progress= false;

                $scope.payment_methods = [
                    {name:'Paypal', method:'paypal'},
                    {name:'Credit Card', method:'credit_card'}
                ];

                $scope.card_types = [
                    {name:'Visa', type:'visa'},
                    {name:'MasterCard', type:'mastercard'},
                    {name:'Discover', type:'discover'},
                    {name:'American Express', type:'american_express'}
                ];

                $scope.payment={
                    amount:1.00,
                    method:'paypal',
                    type:'self'
                };

                $scope.pay = function(){
                  $scope.payment_in_progress= true;

                  var data = angular.copy($scope.payment);

                  if(data.method=='credit_card'){
                      data.credit_card.number = ''+data.credit_card.number;
                  }

                  Payment.create(data).then(
                      function success(response){
                          if(data.method=='credit_card'){
                              $mdToast.showSimple(response.message);
                              $location.url('/profile');
                          }else {
                              $window.location.href = response[0].redirect_url;
                          }
                      },
                      function error(response){
                          $mdToast.showSimple('Error during payment. Please try again.');
                      }
                  ).finally(function () {
                        $scope.payment_in_progress= false;
                    });
                };

                $scope.hide = function() {
                    $mdDialog.hide();
                };
                $scope.cancel = function() {
                    $mdDialog.cancel();
                };


            }
        }
    }
})();