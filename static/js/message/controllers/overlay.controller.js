/**
 * OverlayController
 * @namespace crowdsource.message.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.message.controllers')
        .controller('OverlayController', OverlayController);

    OverlayController.$inject = ['Message', 'Overlay', '$rootScope', '$stateParams', '$scope', '$state', 'User', '$filter', '$timeout'];

    /**
     * @namespace OverlayController
     */

    function OverlayController(Message, Overlay, $rootScope, $stateParams, $scope, $state, User, $filter, $timeout) {
        var self = this;

        self.conversation = null;
        self.recipient = null;
        self.loading = true;

        self.isConnected = false;
        self.isExpanded = false;

        self.scrollBottom = scrollBottom;
        self.initializeWebSocket = initializeWebSocket;
        self.getIcon = getIcon;
        self.toggle = toggle;
        self.sendMessage = sendMessage;
        self.closeConversation = closeConversation;
        self.status = {
            OPEN: 1,
            MINIMIZED: 2,
            CLOSED: 3,
            MUTED: 4
        };

        activate();

        function activate() {
            $scope.$on('overlay', function (event, requester) {
                handleNewOverlay(requester, true);
            });

            self.isConnected = Overlay.isConnected;
            self.isExpanded = Overlay.isExpanded;

            self.initializeWebSocket(receiveMessage);

            if (self.isConnected) {
                var recipient = Overlay.recipient.alias;
                handleNewOverlay(recipient, Overlay.isExpanded);
            }
        }

        function getIcon() {
            return self.isExpanded ? 'close' : '';
        }

        function toggle(open, e) {
            self.isExpanded = (open != null) ? open : !self.isExpanded;
            if (e && $(e.target).hasClass('_toggle'))
                return;
            Overlay.isExpanded = self.isExpanded;

            if (self.isExpanded) {
                getConversation();
                scrollBottom();
            }
            var status = self.isExpanded ? self.status.OPEN : self.status.MINIMIZED;
            updateConversation(status);

        }

        function updateConversation(status) {
            if (!self.conversation) return;
            Message.updateConversation(self.conversation.id, status).then(
                function success(data) {

                },
                function error(data) {
                }).finally(function () {

                }
            );
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
                callback(data);
            });
        }

        function handleNewOverlay(requester, isExpanded) {
            self.conversation = null;

            User.getProfile(requester).then(function (response) {
                self.recipient = {
                    user_id: response[0].user,
                    alias: requester
                };

                Overlay.recipient = self.recipient;

                self.isConnected = true;
                Overlay.isConnected = self.isConnected;

                toggle(isExpanded);
            });
        }

        function scrollBottom() {
            $timeout(function () {
                var messageDiv = $('._overlay-messages');
                messageDiv.animate({scrollTop: messageDiv[0].scrollHeight}, 1000, 'swing');
            }, 0, false);
        }

        function closeConversation(e) {
            e.preventDefault();
            self.isConnected = false;
            Overlay.isConnected = self.isConnected;
            updateConversation(self.status.CLOSED);
        }
    }

})
();
