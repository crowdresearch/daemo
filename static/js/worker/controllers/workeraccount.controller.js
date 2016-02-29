/**
 * WorkerAccountController
 * @namespace crowdsource.worker.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.worker.controllers')
        .controller('WorkerAccountController', WorkerAccountController);

    WorkerAccountController.$inject = ['$state', '$scope',
        '$stateParams', '$mdToast', 'Authentication', 'Worker', 'Skill'];

    /**
     * @namespace WorkerAccountController
     */
    function WorkerAccountController($state, $scope,
                                     $stateParams, $mdToast, Authentication, Worker, Skill) {

        var vm = this;
        var userAccount = Authentication.getAuthenticatedAccount();

        Skill.getAllSkills().then(function (skillsData) {
            vm.skills = skillsData[0].map(function (skill) {
                return {
                    value: skill,
                    display: skill.name
                };
            });
            getWorkerPrivatePortfolio();
        });

        $scope.removeSkill = function removeSkill(skill) {
            Worker.removeSkill(skill.value.id)
                .then(function success(data) {
                    getWorkerPrivatePortfolio();
                }, function (err) {
                    $mdToast.showSimple('Error removing skill');
                });
        };

        function getErrorStr(form) {
            var errorStr = [];
            if (form.$error.required.length) {
                form.$error.required.forEach(function (err) {
                    errorStr.push(err.$name + ' is invalid');
                });
            }
            return errorStr.join(',');
        }

        function getWorkerPrivatePortfolio() {
            Worker.getWorkerPrivateProfile(userAccount.username)
                .then(function (resp) {

                    $scope.user = resp[0];
                    // Make worker id specific
                    $scope.user.workerId = $scope.user.id;
                    var refinedSkills = [];
                    $scope.user.skills.forEach(function (skillId) {
                        vm.skills.forEach(function (skillEntry) {
                            if (skillId === skillEntry.value.id) {
                                refinedSkills.push(skillEntry);
                            }
                        });
                    });
                    $scope.user.skills = refinedSkills;
                }, function error(resp) {
                    var errorMsg = resp[0];
                    $mdToast.showSimple('Error getting worker ' + errorMsg);
                });
        }

        vm.simulateQuery = false;
        vm.isDisabled = false;

        vm.querySearch = querySearch;
        vm.selectedItemChange = selectedItemChange;
        vm.searchTextChange = searchTextChange;

        // ******************************
        // Internal methods
        // ******************************

        /**
         * Search for states... use $timeout to simulate
         * remote dataservice call.
         */
        function querySearch(query) {
            var results = query ? vm.skills.filter(createFilterFor(query)) : vm.skills,
                deferred;
            if (vm.simulateQuery) {
                deferred = $q.defer();
                $timeout(function () {
                    deferred.resolve(results);
                }, Math.random() * 1000, false);
                return deferred.promise;
            } else {
                return results;
            }
        }

        function searchTextChange(text) {
            // pass
        }

        function selectedItemChange(item) {
            if (!item || !item.value) {
                return;
            }
            var skillExists = false;
            $scope.user.skills.forEach(function (skillObj) {
                if (skillObj.id === item.value.id) {
                    $mdToast.showSimple('You\'ve already added this skill!');
                    skillExists = true;
                }
            });
            if (skillExists) {
                return;
            }

            Worker.addSkill(item.value.id)
                .then(function success(data) {
                    vm.searchText = '';
                    getWorkerPrivatePortfolio();
                }, function (err) {
                    $mdToast.showSimple('Error adding skill');
                });
        }

        /**
         * Create filter function for a query string
         */
        function createFilterFor(query) {
            var lowercaseQuery = angular.lowercase(query);

            return function filterFn(skill) {
                return (skill.value.indexOf(lowercaseQuery) === 0);
            };

        }


    }
})();