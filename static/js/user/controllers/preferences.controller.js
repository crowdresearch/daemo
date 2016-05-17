/**
 * PreferencesController
 * @namespace crowdsource.user.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.user.controllers')
        .controller('PreferencesController', PreferencesController);

    PreferencesController.$inject = ['$state', '$scope', '$window', '$mdToast', 'User'];

    /**
     * @namespace PreferencesController
     */
    function PreferencesController($state, $scope, $window, $mdToast, User) {
        var self = this;
        self.searchTextChange = searchTextChange;
        self.selectedItemChange = selectedItemChange;
        self.querySearch = querySearch;
        self.blockedUsers = ['aydam', 'dmorina', 'msb', 'julia', 'alessia', 'matt', 'jon', 'thomas', 'bran', 'walter',
            'aydam1', 'dmorina1', 'msb1', 'julia1', 'alessia1', 'matt1', 'jon1', 'thomas1', 'bran1', 'walter1',
            'aydam2', 'dmorina2', 'msb2', 'julia2', 'alessia2', 'matt2', 'jon2', 'thomas2', 'bran2', 'walter2',
            'aydam3', 'dmorina3', 'msb3', 'julia3', 'alessia3', 'matt3', 'jon3', 'thomas3', 'bran3', 'walter3'];

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
    }
})();
