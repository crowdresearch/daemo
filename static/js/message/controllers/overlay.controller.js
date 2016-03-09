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
        self.conversations = [];
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
            listOpen();
        }

        function getIcon(conversation_rec) {
            return conversation_rec.isExpanded ? 'close' : '';
        }

        function listOpen() {
            if (!Overlay.openConversations) {
                Message.listOpenConversations().then(
                    function success(data) {
                        Overlay.openConversations = data[0];
                        self.conversations = Overlay.openConversations;
                    },
                    function error(data) {
                    }).finally(function () {

                    }
                );
            }
        }

        function toggle(open, e, conversation) {
            conversation.isExpanded = (open != null) ? open : !conversation.isExpanded;
            if (e && $(e.target).hasClass('_toggle'))
                return;
            Overlay.isExpanded = conversation.isExpanded;

            if (conversation.isExpanded) {
                listMessages(conversation);
            }
            var status = conversation.isExpanded ? self.status.OPEN : self.status.MINIMIZED;
            updateConversation(status, conversation);

        }

        function updateConversation(status, conversation) {
            if (!conversation) return;
            Message.updateConversation(conversation.conversation.id, status).then(
                function success(data) {
                },
                function error(data) {
                }).finally(function () {

                }
            );
        }

        function createConversation() {
            Message.createConversation([self.recipient.user_id], null).then(
                function success(data) {
                    self.conversations.push(data[0]);
                    listMessages(data[0]);
                },
                function error(data) {
                }).finally(function () {

                }
            );
        }

        function listMessages(conversation_rec) {
            if (!conversation_rec.conversation.hasOwnProperty('messages')) {
                Message.listMessages(conversation_rec.conversation.id).then(
                    function success(data) {
                        angular.extend(conversation_rec.conversation, {messages: data[0]});
                        self.loading = false;
                        scrollBottom(conversation_rec.id);
                    },
                    function error(data) {
                    }).finally(function () {

                    }
                );
            }

        }

        function receiveMessage(message) {
            angular.extend(message, {is_self: false});
            var conversation = $filter('filter')(self.conversations, function (obj) {
                return obj.conversation.id == message.conversation;
            });
            if (!conversation.length) {
                return;
            }
            if (!conversation[0].conversation.hasOwnProperty('messages')) {
                angular.extend(conversation[0].conversation, {messages: []});
            }
            conversation[0].conversation.messages.push(message);
            $scope.$apply();
            scrollBottom(conversation[0].id);
        }

        function sendMessage(conversation) {
            Message.sendMessage(conversation.newMessage, conversation.conversation.recipient_names[0],
                conversation.conversation.id).then(
                function success(data) {
                    var conversation = $filter('filter')(self.conversations, function (obj) {
                        return obj.conversation.id == data[0].conversation;
                    });
                    if (!conversation[0].conversation.hasOwnProperty('messages'))
                        angular.extend(conversation[0].conversation, {'messages': []});
                    conversation[0].conversation.messages.push(data[0]);
                    conversation[0].newMessage = null;
                    scrollBottom(conversation[0].id);

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

        function scrollBottom(conversation_id) {
            $timeout(function () {
                var messageDiv = $('._c' + conversation_id + ' > ._overlay-messages');
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
