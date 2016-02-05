/**
 * MessageController
 * @namespace crowdsource.message.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.message.controllers')
        .controller('MessageController', MessageController);

    MessageController.$inject = ['Message', '$websocket', '$rootScope', '$routeParams', '$scope'];

    /**
     * @namespace MessageController
     */
    function MessageController(Message, $websocket, $rootScope, $routeParams, $scope) {

        var self = this;
        self.loading = false;
        self.selectedThread = null;
        self.activeRecipient = null;
        self.messages = [];
        self.conversations = [];
        self.sendMessage = sendMessage;
        self.newMessage = null;
        activate();

        function activate() {
            self.activeRecipient = '@' + $routeParams.username;
            Message.listConversations().then(
                function success(data) {
                    self.conversations = data[0];
                    if (self.conversations.length) {
                        self.selectedThread = self.conversations[0];
                        Message.listMessages(self.conversations[0].id).then(
                            function success(data) {
                                self.selectedThread.messages = data[0];
                                initializeWebSocket();
                            },
                            function error(data) {
                            }).finally(function () {

                            }
                        );

                    }
                },
                function error(data) {
                    //$mdToast.showSimple('Could not skip task.');
                }).finally(function () {

                }
            );

        }

        function sendMessage() {
            Message.sendMessage(self.newMessage, $routeParams.username, self.selectedThread.id).then(
                function success(data) {
                    self.selectedThread.messages.push(data[0]);
                    self.selectedThread.last_message.body = data[0].body;
                    self.newMessage = null;
                    //$scope.$apply();
                },
                function error(data) {
                    //$mdToast.showSimple('Could not skip task.');
                }).finally(function () {
                    scrollBottom();
                }
            );
        }

        function initializeWebSocket() {
            self.ws = $websocket.$new({
                url: $rootScope.getWebsocketUrl() + '/ws/inbox?subscribe-user',
                lazy: true,
                reconnect: true
            });
            self.ws
                .$on('$message', function (data) {
                    var message = JSON.parse(data);
                    angular.extend(message, {is_self: false});
                    if (self.selectedThread) {
                        self.selectedThread.messages.push(message);
                        self.selectedThread.last_message.body = message.body;
                        $scope.$apply();
                        scrollBottom();
                    }
                })
                .$on('$close', function () {
                    console.log('Web-socket closed');
                })
                .$on('$open', function () {
                    console.log('Web-socket opened!');
                    //ws.$close();
                })
                .$open();
        }

        function scrollBottom() {
            var messageDiv = $('._task-submissions');
            messageDiv.scrollTop(messageDiv[0].scrollHeight);
        }
    }

})
();
