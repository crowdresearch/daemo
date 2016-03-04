/**
 * OverlayController
 * @namespace crowdsource.message.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.message.controllers')
        .controller('OverlayController', OverlayController);

    OverlayController.$inject = ['Message', '$rootScope', '$stateParams', '$scope', '$state', 'User', '$filter', '$timeout'];

    /**
     * @namespace OverlayController
     */

    function OverlayController(Message, $rootScope, $stateParams, $scope, $state, User, $filter, $timeout) {
        var self = this;

        self.scrollBottom = scrollBottom;
        self.initializeWebSocket = initializeWebSocket;
        self.isExpanded = false;
        self.conversation = null;
        self.getIcon = getIcon;
        self.toggle = toggle;
        self.recipient = null;
        self.loading = true;
        self.sendMessage = sendMessage;
        self.closeConversation = closeConversation;
        activate();

        function activate() {
            //self.recipient = $scope.task.taskData.project_data.owner;
            self.initializeWebSocket(receiveMessage);
        }

        function getIcon() {
            return self.isExpanded ? 'close' : '';
        }

        function toggle(open) {
            self.isExpanded = open ? true : !self.isExpanded;
            getConversation();
            scrollBottom();
        }

        function getConversation() {
            if (!self.conversation) {
                Message.createConversation([self.recipient.user_id], null).then(
                    function success(data) {
                        self.conversation = data[0];
                        listMessages();
                    },
                    function error(data) {
                    }).finally(function () {

                    }
                );
            }
        }

        function listMessages() {
            Message.listMessages(self.conversation.id).then(
                function success(data) {
                    self.conversation.messages = data[0];
                    self.loading = false;
                },
                function error(data) {
                }).finally(function () {

                }
            );
        }

        function receiveMessage(message) {
            angular.extend(message, {is_self: false});
            if (message.conversation != self.conversation.id) {
                return;
            }
            if (self.conversation.hasOwnProperty('messages')) {
                self.conversation.messages.push(message);
            }
            self.conversation.last_message.body = message.body;
            $scope.$apply();
            scrollBottom();
        }

        function sendMessage() {
            Message.sendMessage(self.newMessage, self.recipient.alias, self.conversation.id).then(
                function success(data) {
                    if (!self.conversation.hasOwnProperty('messages'))
                        angular.extend(self.conversation, {'messages': []});
                    self.conversation.messages.push(data[0]);
                    self.conversation.last_message.body = data[0].body;
                    self.conversation.last_message.time_relative = data[0].time_relative;
                    self.newMessage = null;
                    scrollBottom();
                },
                function error(data) {
                }).finally(function () {

                }
            );
        }

        function initializeWebSocket(callback) {
            $scope.$on('message', function (event, data) {
                console.log(data);
                callback(data);
            });

            //self.ws = $websocket.$new({
            //    url: $rootScope.getWebsocketUrl() + '/ws/inbox?subscribe-user',
            //    lazy: true,
            //    reconnect: true
            //});
            //self.ws
            //    .$on('$message', function (data) {
            //        callback(data);
            //    })
            //    .$on('$close', function () {
            //
            //    })
            //    .$on('$open', function () {
            //        console.log("overlay open");
            //    })
            //    .$open();
        }

        function scrollBottom() {
            $timeout(function () {
                var messageDiv = $('._overlay-messages');
                messageDiv.scrollTop(messageDiv[0].scrollHeight);
            }, 0, false);
        }

        function closeConversation(e) {
            e.preventDefault();
            self.isExpanded = false;
        }
    }

})
();
