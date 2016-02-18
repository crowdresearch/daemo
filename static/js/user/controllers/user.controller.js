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

        var userAccount = Authentication.getAuthenticatedAccount();
        if (!userAccount) {
            $location.path('/login');
            return;
        }

        vm.initialize = initialize;
        vm.update = update;
        vm.paypal_payment = paypal_payment;
        vm.searchText = null;
        vm.querySearch = querySearch;

        initialize();

        function initialize() {
            vm.genders = [
                {key: "M", value: "Male"},
                {key: "F", value: "Female"},
                {key: "O", value: "Other"}
            ];
            vm.ethnicities = [
                {key: "white", value: "White"},
                {key: "hispanic", value: "Hispanic"},
                {key: "black", value: "Black"},
                {key: "islander", value: "Native Hawaiian or Other Pacific Islander"},
                {key: "indian", value: "Indian"},
                {key: "asian", value: "Asian"},
                {key: "native", value: "Native American or Alaska Native"}
            ];

            User.getCountries().then(function (response) {
                vm.countries = response.data;
            });

            User.getCities().then(function (response) {
                vm.cities = response.data;
            });

            User.getJobTitles().then(function (response) {
                vm.job_titles = response.data;
            });

            getProfile();
        }

        function getProfile(){
            User.getProfile(userAccount.username)
                .then(function (data) {
                    var user = data[0];

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

                    user.first_name = userAccount.first_name;
                    user.last_name = userAccount.last_name;
                    vm.user = user;
                    vm.user.birthday = new Date(user.birthday);
                    vm.user.gender = _.find(vm.genders, function (gender) {
                        return gender.key == vm.user.gender;
                    });
                    vm.user.ethnicity = _.find(vm.ethnicities, function (ethnicity) {
                        return ethnicity.key == vm.user.ethnicity;
                    });
                    vm.user.workerId = user.id;     // Make worker id specific

                    var address = [];
                    if (vm.user.address.street) {
                        address.push(vm.user.address.street);
                    }
                    if (vm.user.address.city) {
                        address.push(vm.user.address.city.name);
                    }
                    if (vm.user.address.country) {
                        address.push(vm.user.address.country.name);
                    }
                    vm.user.address_text = address.join(", ");
                });
        }

        function querySearch(query) {
            return query ? _.filter(vm.job_titles, function(job_title){
                return (angular.lowercase(job_title).indexOf(angular.lowercase(query)) !== -1)
            }) : vm.job_titles;
        }

        function update() {
            var user = angular.copy(vm.user);

            if (user.gender) {
                user.gender = user.gender.key;
            }

            if (user.ethnicity) {
                user.ethnicity = user.ethnicity.key;
            }

            User.updateProfile(userAccount.username, user)
                .then(function (data) {
                    getProfile();
                    vm.edit=false;
                    $mdToast.showSimple('Profile updated');
                });
        }

        function paypal_payment($event) {
            $mdDialog.show({
                clickOutsideToClose: false,
                preserveScope: false,
                targetEvent: $event,
                templateUrl: '/static/templates/payment/payment.html',
                locals: {
                    dialog: $mdDialog
                },
                controller: DialogController
            });

            function DialogController($scope, dialog) {

                $scope.payment_in_progress = false;

                $scope.payment_methods = [
                    {name: 'Paypal', method: 'paypal'},
                    {name: 'Credit Card', method: 'credit_card'}
                ];

                $scope.card_types = [
                    {name: 'Visa', type: 'visa'},
                    {name: 'MasterCard', type: 'mastercard'},
                    {name: 'Discover', type: 'discover'},
                    {name: 'American Express', type: 'american_express'}
                ];

                $scope.payment = {
                    amount: 1.00,
                    method: 'paypal',
                    type: 'self'
                };

                $scope.$watch('payment.method', function (newValue, oldValue) {
                    if (newValue != oldValue && newValue == 'paypal') {
                        if ($scope.payment.hasOwnProperty('credit_card')) {
                            delete $scope.payment.credit_card;
                        }
                    }
                });

                $scope.pay = function () {
                    $scope.payment_in_progress = true;

                    var data = angular.copy($scope.payment);

                    if (data.method == 'credit_card') {
                        data.credit_card.number = '' + data.credit_card.number;
                    }

                    Payment.create(data).then(
                        function success(response) {
                            if (data.method == 'credit_card') {
                                $mdToast.showSimple(response.message);
                                $location.url('/profile');
                            } else {
                                $window.location.href = response[0].redirect_url;
                            }
                        },
                        function error(response) {
                            $mdToast.showSimple('Error during payment. Please try again.');
                        }
                    ).finally(function () {
                            $scope.payment_in_progress = false;
                        });
                };

                $scope.hide = function () {
                    dialog.hide();
                };
                $scope.cancel = function () {
                    dialog.cancel();
                };


            }
        }
    }
})();