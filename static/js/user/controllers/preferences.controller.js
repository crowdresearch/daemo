/**
 * PreferencesController
 * @namespace crowdsource.user.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.user.controllers')
        .controller('PreferencesController', PreferencesController);

    PreferencesController.$inject = ['$state', '$scope', '$window', '$mdToast', 'User', '$filter'];

    /**
     * @namespace PreferencesController
     */
    function PreferencesController($state, $scope, $window, $mdToast, User, $filter) {
        var self = this;
        self.searchTextChange = searchTextChange;
        self.selectedItemChange = selectedItemChange;
        self.querySearch = querySearch;
        self.createBlackList = createBlackList;
        self.retrieveBlackList = retrieveBlackList;
        self.unblockWorker = unblockWorker;
        self.blockWorker = blockWorker;
        self.black_list_entries = [];
        self.black_list = null;
        self.blockedUsers = ['aydam', 'dmorina', 'msb', 'julia', 'alessia', 'matt', 'jon', 'thomas', 'bran', 'walter',
            'aydam1', 'dmorina1', 'msb1', 'julia1', 'alessia1', 'matt1', 'jon1', 'thomas1', 'bran1', 'walter1',
            'aydam2', 'dmorina2', 'msb2', 'julia2', 'alessia2', 'matt2', 'jon2', 'thomas2', 'bran2', 'walter2',
            'aydam3', 'dmorina3', 'msb3', 'julia3', 'alessia3', 'matt3', 'jon3', 'thomas3', 'bran3', 'walter3',
            'aydam4', 'dmorina4', 'msb4', 'julia4', 'alessia4', 'matt4', 'jon4', 'thomas4', 'bran4', 'walter4',
            'aydam5', 'dmorina5', 'msb5', 'julia5', 'alessia5', 'matt5', 'jon5', 'thomas5', 'bran5', 'walter5'
        ];

        function activate() {

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
                    if (!self.black_list) {
                        createBlackList();
                        return;
                    }
                    getListEntries();
                }
            );
        }

        function getListEntries() {
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
