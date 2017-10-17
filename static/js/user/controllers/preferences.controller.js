/**
 * PreferencesController
 * @namespace crowdsource.user.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.user.controllers')
        .controller('PreferencesController', PreferencesController);

    PreferencesController.$inject = ['$state', '$scope', '$window', '$mdToast', 'User', '$filter',
        'Authentication', '$mdDialog'];

    /**
     * @namespace PreferencesController
     */
    function PreferencesController($state, $scope, $window, $mdToast, User, $filter, Authentication, $mdDialog) {
        var self = this;
        self.searchTextChange = searchTextChange;
        self.selectedItemChange = selectedItemChange;
        self.querySearch = querySearch;
        self.createBlackList = createBlackList;
        self.retrieveBlackList = retrieveBlackList;
        var userAccount = Authentication.getAuthenticatedAccount();
        self.unblockWorker = unblockWorker;
        self.blockWorker = blockWorker;
        self.black_list_entries = [];
        self.workerGroups = [];
        self.groupMembers = [];
        self.workers = [];
        self.newWorkerGroup = {};
        self.black_list = null;
        self.selectedGroupMember = null;
        self.loading = false;
        self.openWorkerGroupNew = openWorkerGroupNew;
        self.addWorkerGroup = addWorkerGroup;
        self.addWorkerToGroup = addWorkerToGroup;
        self.removeWorkerFromGroup = removeWorkerFromGroup;
        activate();

        $scope.$watch('preferences.workerGroup', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue)) {
                self.groupMembers = [];
                User.retrieveRequesterListEntries(newValue).then(function success(response) {
                    self.groupMembers = response[0];
                });
            }

        });

        function activate() {
            self.loading = true;

            if ($state.current.name === 'unsubscribe') {
                User.updatePreferences(userAccount.username, {'new_tasks_notifications': false}).then(function () {
                });
            }
            else {
                listWorkerGroups();
                retrieveBlackList();
            }

        }


        function querySearch(query) {
            return User.listWorkers(query).then(
                function success(data) {
                    return data[0];
                }
            );
        }

        function searchTextChange(text) {
        }

        function selectedItemChange(item) {
        }

        function createBlackList() {
            User.createRequesterBlackList().then(
                function success(data) {
                    self.black_list = data[0];
                    getListEntries();
                }
            );
        }

        function retrieveBlackList() {
            User.retrieveRequesterBlackList().then(
                function success(data) {
                    self.black_list = data[0];
                    self.loading = false;
                    if (!self.black_list.id) {
                        createBlackList();
                        return;
                    }
                    getListEntries();
                }
            );
        }

        function getListEntries() {
            if (!self.black_list.id) {
                return;
            }
            User.retrieveRequesterListEntries(self.black_list.id).then(
                function success(data) {
                    self.black_list_entries = data[0];
                }
            );
        }

        function blockWorker() {
            var data = {
                "group": self.black_list.id,
                "worker": self.selectedItem.worker ? self.selectedItem.worker : self.selectedItem.id
            };
            User.createRequesterListEntry(data).then(
                function success(data) {
                    var justAdded = $filter('filter')(self.black_list_entries, {'handle': data[0].handle}, true);
                    if (justAdded.length) {
                        justAdded[0].id = data[0].id;
                        justAdded[0].group = data[0].group;
                        justAdded[0].worker = data[0].worker;
                    }
                    self.selectedItem = null;
                    self.searchText = null;
                }
            );
        }

        function unblockWorker(entry) {
            User.deleteRequesterListEntry(entry.id).then(
                function success(data) {
                }
            );
        }

        function listWorkerGroups() {
            User.listFavoriteGroups().then(
                function success(data) {
                    self.workerGroups = data[0];
                }
            );
        }

        function openWorkerGroupNew($event) {
            var parent = angular.element(document.body);
            $mdDialog.show({
                clickOutsideToClose: true,
                scope: $scope,
                preserveScope: true,
                parent: parent,
                targetEvent: $event,
                templateUrl: '/static/templates/project/new-worker-group.html',
                controller: DialogController
            });
        }

        function DialogController($scope, $mdDialog) {
            $scope.hide = function () {
                $mdDialog.hide();
            };
            $scope.cancel = function () {
                $mdDialog.cancel();
            };
        }

        function addWorkerGroup() {
            // if (self.workerGroup.members.length == 0) {
            //     self.workerGroup.error = 'You must select at least one worker.';
            //     return;
            // }
            if (!self.newWorkerGroup.name) {
                self.newWorkerGroup.error = 'Enter a group name.';
                return;
            }
            // var entries = [];
            // angular.forEach(self.workerGroup.members, function (obj) {
            //     entries.push(obj.id);
            // });
            var data = {
                name: self.newWorkerGroup.name,
                type: 1,
                is_global: false,
                "entries": []
            };

            User.createGroupWithMembers(data).then(
                function success(data) {
                    self.workerGroups.push(data[0]);
                    self.newWorkerGroup.name = 'Untitled Group';
                    self.newWorkerGroup.error = null;
                    self.newWorkerGroup.members = [];
                    $scope.cancel();
                }
            );

        }

        function addWorkerToGroup($chip) {
            var workerId = $chip.worker ? $chip.worker : $chip.id;
            var data = {
                "group": self.workerGroup,
                "worker": workerId
            };
            User.createRequesterListEntry(data).then(
                function success(data) {
                    var justAdded = $filter('filter')(self.groupMembers, {'handle': data[0].handle}, true);
                    if (justAdded.length) {
                        justAdded[0].id = data[0].id;
                        justAdded[0].group = data[0].group;
                        justAdded[0].worker = data[0].worker;
                    }
                    self.selectedGroupMember = null;
                    self.searchTextForGroup = null;
                }
            );
        }

        function removeWorkerFromGroup($chip) {
            User.deleteRequesterListEntry($chip.id).then(
                function success(data) {
                }
            );
        }
    }
})();
