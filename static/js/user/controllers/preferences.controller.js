/**
 * PreferencesController
 * @namespace crowdsource.user.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.user.controllers')
        .controller('PreferencesController', PreferencesController);

    PreferencesController.$inject = ['$state', '$scope', '$window', '$mdToast', 'User', '$filter', 'Authentication'];

    /**
     * @namespace PreferencesController
     */
    function PreferencesController($state, $scope, $window, $mdToast, User, $filter, Authentication) {
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
        self.black_list = null;
        activate();
        function activate() {
            console.log('nunsubs');
            console.log($state.current.name);
            if ($state.current.name === 'unsubscribe') {
                User.updatePreferences(userAccount.username, {'new_tasks_notifications': false}).then(function () {
                });
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
                "worker": self.selectedItem.id
            };
            User.createRequesterListEntry(data).then(
                function success(data) {
                    self.black_list_entries.unshift(data[0]);
                    self.selectedItem = null;
                    self.searchText = null;
                }
            );
        }

        function unblockWorker(entry) {
            User.deleteRequesterListEntry(entry.id).then(
                function success(data) {
                    var entry = $filter('filter')(self.black_list_entries, {'id': data[0].pk});
                    var index = self.black_list_entries.indexOf(entry[0]);
                    self.black_list_entries.splice(index, 1);
                }
            );
        }
    }
})();
