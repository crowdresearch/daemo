/**
 * Register controller
 * @namespace crowdsource.authentication.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.authentication.controllers')
        .controller('RegisterController', ['$state', '$scope', 'Authentication', '$mdToast', '$q',
            function RegisterController($state, $scope, Authentication, $mdToast, $q) {

                activate();

                function activate() {
                    // If the user is authenticated, they should not be here.
                    if (Authentication.isAuthenticated()) {
                        $state.go('profile');
                    }
                }

                var self = this;

                self.register = register;
                self.addressSearch = addressSearch;
                self.addressSearchValue = null;
                self.getAddress = getAddress;
                self.errors = [];
                self.registrationEnabled = true;

                // var PlaceService = new google.maps.places.AutocompleteService();

                /**
                 * @name register
                 * @desc Register a new user
                 * @memberOf crowdsource.authentication.controllers
                 */
                function register(isValid) {
                    if (isValid) {
                        Authentication.register(self.email, self.firstname, self.lastname,
                            self.password1, self.password2, self.location, self.birthday).then(function () {
                            $mdToast.showSimple('Email with an activation link has been sent.');
                            $state.go('auth.login');
                        }, function (data, status) {
                            
                            if (data.status === 403) {
                                self.registrationEnabled = false;
                                return;
                            }

                            //Global errors
                            if (data.data.hasOwnProperty('detail')) {
                                self.error = data.data.detail;
                                $scope.form.$setPristine();
                            }

                            angular.forEach(data.data, function (errors, field) {

                                if (field == 'non_field_errors') {
                                    self.error = errors.join(', ');
                                    $scope.form.$setPristine();
                                } else {
                                    $scope.form[field].$setValidity('backend', false);
                                    $scope.form[field].$dirty = true;
                                    if (errors[0] === "This field must be unique.") {
                                        self.errors[field] = "This email address is already registered.";
                                    }
                                    else {
                                        self.errors[field] = errors.join(', ');
                                    }

                                }
                            });

                        }).finally(function () {
                        });
                    }
                    self.submitted = true;
                }

                function addressSearch(address) {
                    // var deferred = $q.defer();
                    // getResults(address).then(
                    //     function (predictions) {
                    //         var results = [];
                    //         for (var i = 0, prediction; prediction = predictions[i]; i++) {
                    //             results.push(prediction);
                    //         }
                    //         deferred.resolve(results);
                    //     }
                    // );
                    // return deferred.promise;
                }

                function getResults(address) {
                    // var deferred = $q.defer();
                    // if (address) {
                    //     PlaceService.getPlacePredictions({input: address}, function (data) {
                    //         deferred.resolve(data);
                    //     });
                    // } else {
                    //     deferred.resolve('');
                    // }
                    // return deferred.promise;
                }

                function getAddress() {
                    // if (self.addressSearchValue !== "" && self.address_text === null) {
                    //     self.autocompleteError = true;
                    //     return;
                    // }
                    // if (self.addressSearchValue !== "" && self.address_text.place_id !== undefined) {
                    //     var service = new google.maps.places.PlacesService(document.getElementById('node'));
                    //     service.getDetails({placeId: self.address_text.place_id}, function (result, status) {
                    //         var street_number = "";
                    //         var street = "";
                    //         console.log(result.address_components);
                    //         self.location = {};
                    //         var city = _.find(result.address_components,
                    //             function (address_component) {
                    //                 return address_component.types.includes("locality")
                    //             });
                    //         if (city !== undefined) {
                    //             self.location.city = city.long_name
                    //         }
                    //
                    //         var country = _.find(result.address_components,
                    //             function (address_component) {
                    //                 return address_component.types.includes("country")
                    //             });
                    //         if (country !== undefined) {
                    //             self.location.country = country.long_name;
                    //             self.location.country_code = country.short_name;
                    //         }
                    //
                    //         var state = _.find(result.address_components,
                    //             function (address_component) {
                    //                 return address_component.types.includes("administrative_area_level_1")
                    //             });
                    //         var postal_code = _.find(result.address_components, function (address_component) {
                    //             return address_component.types.includes("postal_code")
                    //         });
                    //         if(postal_code !== undefined){
                    //             self.location.postal_code = postal_code.long_name;
                    //         }
                    //         if (state !== undefined) {
                    //             self.location.state = state.long_name;
                    //             self.location.state_code = state.short_name;
                    //         }
                    //
                    //
                    //         var street_number_component = _.find(result.address_components,
                    //             function (address_component) {
                    //                 return address_component.types.includes("street_number")
                    //             });
                    //         if (street_number_component !== undefined) {
                    //             street_number = street_number_component.long_name;
                    //         }
                    //
                    //         var street_component = _.find(result.address_components,
                    //             function (address_component) {
                    //                 return address_component.types.includes("route")
                    //             });
                    //         if (street_component !== undefined) {
                    //             street = street_component.long_name;
                    //         }
                    //
                    //         if (self.location.city === undefined || self.location.country === undefined) {
                    //             self.autocompleteError = true;
                    //             return;
                    //         }
                    //         self.autocompleteError = false;
                    //         if (street_number === "" && street !== "") {
                    //             self.location.address = street;
                    //         } else if (street_number !== "" && street !== "") {
                    //             self.location.address = street_number.concat(" ").concat(street);
                    //         } else {
                    //             self.location.address = "";
                    //         }
                    //     });
                    //
                    // }
                }
            }

        ]);
})();
