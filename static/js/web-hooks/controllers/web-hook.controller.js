(function () {
    'use strict';

    angular
        .module('crowdsource.web-hooks.controllers')
        .controller('WebHookController', WebHookController);

    WebHookController.$inject = ['$scope', '$rootScope', '$state', 'WebHook', '$stateParams', '$mdToast'];

    function WebHookController($scope, $rootScope, $state, WebHook, $stateParams, $mdToast) {
        var self = this;
        self.create = create;
        self.obj = {};
        self.eventObj = null;
        activate();

        function activate() {
            var hookId = $stateParams.pk;
            if (hookId === 'new') {
                self.obj.name = 'Unnamed Webhook';
                self.obj.is_active = true;
                self.obj.content_type = 'application/json';
            }
            else if (hookId) {
                WebHook.retrieve(hookId).then(
                    function success(data) {
                        self.obj = data[0];
                        self.eventObj = self.obj.object + "." + self.obj.event;
                    },
                    function error(response) {

                    });
            }
        }

        function create() {
            if(!self.eventObj){
                $mdToast.showSimple('Please select an event to subscribe to!');
                return;
            }
            var eventObjArr = self.eventObj.split('.');
            self.obj.event = eventObjArr[1];
            self.obj.object = eventObjArr[0];
            if(!self.obj.url || !self.obj.name || !self.obj.event || !self.obj.object){
                $mdToast.showSimple('All fields are required!');
                return;
            }
            if (self.obj.id) {
                return update();
            }
            WebHook.create(self.obj).then(
                function success(data) {
                    $state.go('requester_settings')
                },
                function error(response) {

                });
        }

        function update() {
            WebHook.update(self.obj.id, self.obj).then(
                function success(data) {
                    $state.go('requester_settings')
                },
                function error(response) {

                });
        }

    }
})();
