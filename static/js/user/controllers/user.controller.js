/**
 * UserController
 * @namespace crowdsource.worker.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.user.controllers')
        .controller('UserController', UserController);

    UserController.$inject = ['$state', '$scope', '$window', '$mdToast', '$mdDialog', '$q', 'Authentication', 'User', 'Payment'];

    /**
     * @namespace UserController
     */

    function UserController($state, $scope, $window, $mdToast, $mdDialog, $q, Authentication, User, Payment) {
        var vm = this;

        var userAccount = Authentication.getAuthenticatedAccount();

        var PlaceService = new google.maps.places.AutocompleteService();

        vm.initialize = initialize;
        vm.update = update;
        vm.paypal_payment = paypal_payment;
        vm.searchText = null;
        vm.jobTitleSearch = jobTitleSearch;
        vm.addressSearch = addressSearch;
        vm.paypal_payment = paypal_payment;
        vm.aws_account = null;
        vm.create_or_update_aws = create_or_update_aws;
        vm.removeAWSAccount = removeAWSAccount;
        vm.awsAccountEdit = false;
        vm.AWSError = null;
        vm.autocompleteError = false;
        vm.getCredentials = getCredentials;
        vm.digestCredentials = digestCredentials;
        vm.credentialsDisabled = false;
        vm.updatePartial = updatePartial;
        vm.savePaymentInfo = savePaymentInfo;
        vm.use_for = null;
        vm.payment = {
            is_worker: null,
            is_requester: null,
            bank: {
                account_number: null,
                routing_number: null
            },
            credit_card: {
                number: null,
                first_name: null,
                last_name: null,
                cvv: null,
                exp_month: null,
                exp_year: null
            }
        };

        activate();

        initialize();

        function initialize() {
            vm.genders = [
                {key: "M", value: "Male"},
                {key: "F", value: "Female"},
                {key: "O", value: "Other"},
                {key: "U", value: "Prefer to not specify"}
            ];
            vm.purpose_of_use = [
                {key: "professional", value: "Professional"},
                {key: "research", value: "Research"},
                {key: "personal", value: "Personal"},
                {key: "other", value: "Other"}
            ];
            vm.ethnicities = [
                {key: "white", value: "White"},
                {key: "hispanic", value: "Hispanic"},
                {key: "black", value: "Black"},
                {key: "islander", value: "Native Hawaiian or Other Pacific Islander"},
                {key: "indian", value: "Indian"},
                {key: "asian", value: "Asian"},
                {key: "native", value: "Native American or Alaska Native"},
                {key: "mixed", value: "Mixed Race"},
                {key: "other", value: "Other"},
                {key: "U", value: "Prefer to not specify"}
            ];
            vm.incomes = [
                {key: 'less_1k', value: 'Less than $1,000'},
                {key: '1k', value: '$1,000 - $1,999'},
                {key: '2.5k', value: '$2,500 - $4,999'},
                {key: '5k', value: '$5,000 - $7,499'},
                {key: '7.5k', value: '$7,500 - $9,999'},
                {key: '10k', value: '$10,000 - $14,999'},
                {key: '15k', value: '$15,000 - $24,999'},
                {key: '25k', value: '$25,000 - $39,999'},
                {key: '40k', value: '$40,000 - $59,999'},
                {key: '60k', value: '$60,000 - $74,999'},
                {key: '75k', value: '$75,000 - $99,999'},
                {key: '100k', value: '$100,000 - $149,999'},
                {key: '150k', value: '$150,000 - $199,999'},
                {key: '200k', value: '$200,000 - $299,999'},
                {key: '300k_more', value: '$300,000 or more'}
            ];
            vm.educations = [
                {key: 'some_high', value: 'Some High School, No Degree'},
                {key: 'high', value: 'High School Degree or Equivalent'},
                {key: 'some_college', value: 'Some College, No Degree'},
                {key: 'associates', value: 'Associates Degree'},
                {key: 'bachelors', value: 'Bachelors Degree'},
                {key: 'masters', value: 'Graduate Degree, Masters'},
                {key: 'doctorate', value: 'Graduate Degree, Doctorate'},
                {key: "U", value: "Prefer to not specify"}
            ];

            //User.getCountries().then(function (response) {
            //    vm.countries = _.sortBy(response[0], 'name');
            //});
            //
            //User.getCities().then(function (response) {
            //    vm.cities = _.sortBy(response[0], 'name');
            //});

            // User.getJobTitles().then(function (response) {
            //     vm.job_titles = response.data;
            // });

            getProfile();
        }

        function addressSearch(address) {
            var deferred = $q.defer();
            getResults(address).then(
                function (predictions) {
                    var results = [];
                    for (var i = 0, prediction; prediction = predictions[i]; i++) {
                        results.push(prediction);
                    }
                    deferred.resolve(results);
                }
            );
            return deferred.promise;
        }

        function getResults(address) {
            var deferred = $q.defer();
            if (address) {
                PlaceService.getPlacePredictions({input: address}, function (data) {
                    deferred.resolve(data);
                });
            } else {
                deferred.resolve('');
            }
            return deferred.promise;
        }

        function getProfile() {
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
                    vm.user = angular.copy(user);

                    if (user.birthday) {
                        vm.user.birthday = new Date(user.birthday);
                    } else {
                        vm.user.birthday = null;
                    }

                    vm.user.gender = _.find(vm.genders, function (gender) {
                        return gender.key == vm.user.gender;
                    });

                    vm.user.purpose_of_use = _.find(vm.purpose_of_use, function (purpose) {
                        return purpose.key == vm.user.purpose_of_use;
                    });

                    vm.user.ethnicity = _.find(vm.ethnicities, function (ethnicity) {
                        return ethnicity.key == vm.user.ethnicity;
                    });

                    vm.user.income = _.find(vm.incomes, function (income) {
                        return income.key == vm.user.income;
                    });
                    vm.user.education = _.find(vm.educations, function (education) {
                        return education.key == vm.user.education;
                    });

                    vm.user.workerId = user.id;     // Make worker id specific
                    var address = [];
                    if (vm.user.address) {
                        if (user.address.street) {
                            address.push(vm.user.address.street);
                        }
                        if (vm.user.address.city) {
                            address.push(vm.user.address.city.name);
                            if (vm.user.address.city.state_code) {
                                address.push(vm.user.address.city.state_code);
                            }
                            if (vm.user.address.city.country) {
                                address.push(vm.user.address.city.country.name);
                            }
                        }
                    }
                    //if (vm.user.address && vm.user.address.city) {
                    //    console.log(vm.user.address.city);
                    //    address.push(vm.user.address.city.name);
                    //
                    //    vm.city = _.find(vm.cities, function (city) {
                    //        return city.id == vm.user.address.city.id;
                    //    });
                    //}

                    //if (vm.user.address && vm.user.address.country) {
                    //    console.log(vm.user.address.country);
                    //    address.push(vm.user.address.country.name);
                    //
                    //    vm.country = _.find(vm.countries, function (country) {
                    //        return country.id == vm.user.address.country.id;
                    //    });
                    //}

                    vm.user.address_text = address.join(", ");

                    if (!vm.user.unspecified_responses) {
                        vm.user.unspecified_responses = {};
                    }
                });
        }

        function jobTitleSearch(query) {
            return query ? _.filter(vm.job_titles, function (job_title) {
                return (angular.lowercase(job_title).indexOf(angular.lowercase(query)) !== -1)
            }) : [];
        }

        function update() {
            var user = angular.copy(vm.user);
            delete user.purpose_of_use;
            if (vm.addressSearchValue !== "" && vm.user.address_text === null) {
                vm.autocompleteError = true;
                return;
            }
            if (vm.addressSearchValue !== "" && vm.user.address_text.place_id !== undefined) {
                var service = new google.maps.places.PlacesService(document.getElementById('node'));
                service.getDetails({placeId: vm.user.address_text.place_id}, function (result, status) {
                    var street_number = "";
                    var street = "";
                    user.location = {};
                    var city = _.find(result.address_components,
                        function (address_component) {
                            return address_component.types.includes("locality")
                        });
                    if (city !== undefined) {
                        user.location.city = city.long_name
                    }

                    var country = _.find(result.address_components,
                        function (address_component) {
                            return address_component.types.includes("country")
                        });
                    if (city !== undefined) {
                        user.location.country = country.long_name;
                        user.location.country_code = country.short_name;
                    }

                    var state = _.find(result.address_components,
                        function (address_component) {
                            return address_component.types.includes("administrative_area_level_1")
                        });
                    if (state !== undefined) {
                        user.location.state = state.long_name;
                        user.location.state_code = state.short_name;
                    }

                    var street_number_component = _.find(result.address_components,
                        function (address_component) {
                            return address_component.types.includes("street_number")
                        });
                    if (street_number_component !== undefined) {
                        street_number = street_number_component.long_name;
                    }

                    var street_component = _.find(result.address_components,
                        function (address_component) {
                            return address_component.types.includes("route")
                        });
                    if (street_component !== undefined) {
                        street = street_component.long_name;
                    }

                    if (user.location.city === undefined || user.location.country === undefined) {
                        vm.autocompleteError = true;
                        return;
                    }
                    vm.autocompleteError = false;

                    if (street_number === "" && street !== "") {
                        user.location.address = street;
                    } else if (street_number !== "" && street !== "") {
                        user.location.address = street_number.concat(" ").concat(street);
                    } else {
                        user.location.address = "";
                    }

                    if (user.gender) {
                        user.gender = user.gender.key;
                    }

                    if (user.ethnicity) {
                        user.ethnicity = user.ethnicity.key;
                    }

                    if (user.income) {
                        user.income = user.income.key;
                    }

                    if (user.education) {
                        user.education = user.education.key;
                    }
                    User.updateProfile(userAccount.username, user)
                        .then(function (data) {
                            getProfile();
                            vm.edit = false;
                            $mdToast.showSimple('Profile updated');
                        });
                });
            } else {
                if (vm.addressSearchValue === "") {
                    user.location = {};
                }
                if (user.gender) {
                    user.gender = user.gender.key;
                }
                if (user.ethnicity) {
                    user.ethnicity = user.ethnicity.key;
                }

                if (user.income) {
                    user.income = user.income.key;
                }

                if (user.education) {
                    user.education = user.education.key;
                }
                User.updateProfile(userAccount.username, user)
                    .then(function (data) {
                        getProfile();
                        vm.edit = false;
                        $mdToast.showSimple('Profile updated');
                    });
            }
        }


        function updatePartial() {
            var user = {
                unspecified_responses: {
                    education: vm.user.education.key == 'U',
                    birthday: vm.user.unspecified_responses.birthday,
                    gender: vm.user.gender.key == 'U',
                    ethnicity: vm.user.ethnicity.key == 'U'
                },
                education: vm.user.education.key == 'U' ? null : vm.user.education.key,
                gender: vm.user.gender.key == 'U' ? null : vm.user.gender.key,
                ethnicity: vm.user.ethnicity.key == 'U' ? null : vm.user.ethnicity.key,
                purpose_of_use: vm.user.purpose_of_use ? vm.user.purpose_of_use.key : null,
                birthday: vm.user.unspecified_responses.birthday ? null : vm.user.birthday,
                user: {}
            };


            if (!user.education && !user.unspecified_responses.education
                || !user.gender && !user.unspecified_responses.gender
                || !user.birthday && !user.unspecified_responses.birthday
                || !user.ethnicity && !user.unspecified_responses.ethnicity
            ) {
                $mdToast.showSimple('All fields are required!');
                return;
            }

            User.updateProfile(userAccount.username, user)
                .then(function (data) {
                    $scope.$emit('profileUpdated', {'is_valid': true});
                });
        }

        function activate() {
            User.get_aws_account().then(
                function success(response) {
                    vm.aws_account = response[0];
                },
                function error(response) {

                }
            );
        }

        function create_or_update_aws() {
            if (vm.aws_account.client_secret == null || vm.aws_account.client_id == null) {
                $mdToast.showSimple('Client key and secret are required');
            }
            User.create_or_update_aws(vm.aws_account).then(
                function success(response) {
                    vm.aws_account = response[0];
                    vm.awsAccountEdit = false;
                    vm.AWSError = null;
                },
                function error(response) {
                    vm.AWSError = 'Invalid keys or missing AmazonMechanicalTurkFullAccess policy, please try again.';
                }
            ).finally(function () {

            });
        }

        function removeAWSAccount() {
            User.removeAWSAccount().then(
                function success(response) {
                    vm.aws_account = null;
                    vm.awsAccountEdit = false;
                },
                function error(response) {

                }
            ).finally(function () {

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
                                $state.go('profile');
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

        function digestCredentials(data) {
            User.getToken(data).then(
                function success(response) {
                    var credentials = {
                        client_id: data.client_id,
                        access_token: response[0].access_token,
                        refresh_token: response[0].refresh_token
                    };
                    var a = document.createElement('a');
                    a.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(credentials));
                    a.target = '_blank';
                    a.download = 'credentials.json';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                },
                function error(response) {
                    $mdToast.showSimple('Could not get access token.');
                }
            ).finally(function () {
            });
        }

        function getCredentials($event) {
            $mdDialog.show({
                clickOutsideToClose: false,
                preserveScope: false,
                targetEvent: $event,
                templateUrl: '/static/templates/user/credentials.html',
                locals: {
                    username: vm.user.user_username,
                    credentialsDisabled: vm.credentialsDisabled,
                    dialog: $mdDialog,
                    digestCredentials: digestCredentials
                },
                controller: DialogController
            });

            function DialogController($scope, username, dialog, digestCredentials) {

                $scope.credentials = {
                    username: username,
                    password: ''
                };

                $scope.submit = function () {
                    var data = angular.copy($scope.credentials);
                    User.getClients(data).then(
                        function success(response) {
                            data.grant_type = 'password';
                            data.client_id = response[0].client_id;
                            data.client_secret = response[0].client_secret;
                            digestCredentials(data);
                            $scope.credentialsDisabled = true;
                        },
                        function error(response) {
                            $mdToast.showSimple(response[0].detail);
                        }
                    ).finally(function () {
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

        function savePaymentInfo() {
            if (!vm.use_for) {
                $mdToast.showSimple('All fields are required!');
                return;
            }
            if (vm.use_for == 'is_worker' || vm.use_for == 'is_both') {
                if (!vm.payment.bank.account_number || !vm.payment.bank.routing_number) {
                    $mdToast.showSimple('Bank account number and routing number are required!');
                    return;
                }
                vm.payment.is_worker = true;
            }
            if (vm.use_for == 'is_requester' || vm.use_for == 'is_both') {
                if (!vm.payment.credit_card.number || !vm.payment.credit_card.cvv
                    || !vm.payment.credit_card.first_name || !vm.payment.credit_card.last_name
                    || !vm.payment.credit_card.exp_month || !vm.payment.credit_card.exp_year
                ) {
                    $mdToast.showSimple('Credit card information is missing!');
                    return;
                }
                vm.payment.is_requester = true;
            }

            User.updatePaymentInfo(vm.payment).then(
                function success(response) {
                    $state.go('profile');
                },
                function error(response) {
                    if (response[0].hasOwnProperty("message")){
                        $mdToast.showSimple(response[0].message);
                    }
                    else {
                        $mdToast.showSimple('Something went wrong');
                    }

                }
            ).finally(function () {

            });
        }
    }
})();
