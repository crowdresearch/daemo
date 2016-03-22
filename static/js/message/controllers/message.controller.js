/**
 * MessageController
 * @namespace crowdsource.message.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.message.controllers')
        .controller('MessageController', MessageController);

    MessageController.$inject = ['Message', '$rootScope', '$stateParams', '$scope', '$location', '$state', 'User', '$filter', '$timeout'];

    /**
     * @namespace MessageController
     */
    function MessageController(Message, $rootScope, $stateParams, $scope, $location, $state, User, $filter, $timeout) {

        var self = this;

        self.loading = false;
        self.selectedThread = null;
        self.messages = [];
        self.users = [];
        self.conversations = [];
        self.newMessage = null;
        self.newRecipients = [];
        self.newConversation = null;

        self.initializeWebSocket = initializeWebSocket;
        self.sendMessage = sendMessage;
        self.querySearch = querySearch;
        self.selectedItemChange = selectedItemChange;
        self.searchTextChange = searchTextChange;
        self.transformChip = transformChip;
        self.startConversation = startConversation;
        self.getNewConversationText = getNewConversationText;
        self.setSelected = setSelected;
        self.isSelected = isSelected;
        self.isInputDisabled = isInputDisabled;
        self.cancelNewConversation = cancelNewConversation;


        activate();

        function activate() {
            initializeWebSocket(receiveMessage);
            listConversations();
        }

        function initializeWebSocket(callback) {
            $scope.$on('message', function (event, data) {
                callback(data);
            });
        }

        function listConversations() {
            Message.listConversations().then(
                function success(data) {
                    self.conversations = data[0];

                    if (self.conversations.length) {
                        var user = $stateParams.t;

                        if (user) {
                            var conversation = _.find(self.conversations, function (conversation) {
                                return conversation.recipient_names.indexOf(user) >= 0;
                            });

                            if (conversation == null) {
                                self.selectedThread = self.conversations[0];
                            } else {
                                self.selectedThread = conversation;
                            }

                        } else {
                            setUser(self.conversations[0].recipient_names[0]);
                            self.selectedThread = self.conversations[0];
                        }

                        if (self.selectedThread.hasOwnProperty('id') && self.selectedThread.id) {
                            listMessages(self.selectedThread.id);
                        }
                    }
                },
                function error(data) {
                }).finally(function () {

                }
            );
        }

        function setUser(username) {
            $state.current.reloadOnSearch = false;

            $location.search('t', username);

            $timeout(function () {
                $state.current.reloadOnSearch = undefined;
            });
        }

        function listMessages(conversation_id) {
            Message.listMessages(conversation_id).then(
                function success(data) {
                    self.selectedThread.messages = data[0];
                    scrollBottom();
                },
                function error(data) {
                }).finally(function () {

                }
            );
        }

        function sendMessage() {
            if (!self.newConversation) {
                newMessage();
            }
            else {
                // check if conversation exists with recipient already
                var conversation = _.find(self.conversations, function (conversation) {
                    return conversation.recipient_names.indexOf(self.newRecipients[0].username) >= 0;
                });

                if (conversation != null) {
                    setSelected(conversation);
                    newMessage();
                } else {
                    var recipients = [self.newRecipients[0].id];
                    Message.createConversation(recipients, null).then(
                        function success(data) {
                            self.conversations.unshift(data[0]);
                            self.selectedThread = data[0];
                            self.newConversation = null;
                            setUser(self.selectedThread.recipient_names[0]);
                            newMessage();
                        },
                        function error(data) {
                        }).finally(function () {

                        }
                    );
                }
            }
        }

        function newMessage() {
            Message.sendMessage(self.newMessage, self.selectedThread.recipient_names[0], self.selectedThread.id).then(
                function success(data) {
                    if (!self.selectedThread.hasOwnProperty('messages')) {
                        angular.extend(self.selectedThread, {'messages': []});
                    }

                    self.selectedThread.messages.push(data[0]);
                    self.selectedThread.last_message.body = data[0].body;
                    self.selectedThread.last_message.time_relative = data[0].time_relative;
                    self.newMessage = null;
                },
                function error(data) {
                }).finally(function () {
                    scrollBottom();
                }
            );
        }

        function scrollBottom() {
            $timeout(function () {
                var messageDiv = $('._message-detail');
                messageDiv.animate({scrollTop: messageDiv[0].scrollHeight}, 1000, 'swing');
            }, 10, false);
        }

        function querySearch(query) {
            return User.listUsernames(query).then(
                function success(data) {
                    return data[0];
                }
            );
        }

        function searchTextChange(text) {
        }

        function selectedItemChange(item) {
            //console.log(item);
        }

        function transformChip(chip) {
            if (angular.isObject(chip)) {
                return chip;
            }
            return {name: chip, type: 'new'}
        }

        function startConversation() {
            self.selectedThread = null;
            self.newRecipients = [];
            self.newConversation = {
                prefix: "New message",
                preposition: " to "
            }
        }

        function getNewConversationText() {
            return self.newRecipients.length ? self.newConversation.prefix + self.newConversation.preposition +
            self.newRecipients[0].username : self.newConversation.prefix;
        }

        function setSelected(conversation) {
            self.selectedThread = conversation;
            self.newConversation = null;

            setUser(self.selectedThread.recipient_names[0]);
            listMessages(self.selectedThread.id);

        }

        function isInputDisabled() {
            return (self.newConversation && !self.newRecipients.length) || (!self.newConversation && !self.selectedThread);
        }

        function cancelNewConversation() {
            self.newConversation = null;
            self.selectedThread = self.conversations[0];
        }

        function isSelected(conversation) {
            return angular.equals(self.selectedThread, conversation);
        }

        function receiveMessage(message) {
            angular.extend(message, {is_self: false});

            var conversation = _.find(self.conversations, function (conversation) {
                return conversation.id == message.conversation;
            });

            var conversation_id = null;

            if (conversation != null) {
                if (!conversation.hasOwnProperty('messages') || conversation.messages == null) {
                    conversation.messages = [];
                }

                conversation.messages.push(message);

                if (!conversation.hasOwnProperty('last_message') || conversation.last_message == null) {
                    conversation.last_message = {};
                }

                conversation.last_message.body = message.body;
                conversation_id = conversation.id;
            }
            else {
                var newConversation = {
                    id: message.conversation,
                    last_message: {
                        body: message.body,
                        time_relative: message.time_relative
                    },
                    recipient_names: [message.sender]
                };
                if (!self.conversations.length) {
                    self.selectedThread = newConversation;
                    angular.extend(self.selectedThread, {messages: [message]});
                }
                self.conversations.push(newConversation);
                conversation_id = newConversation.id;
            }

            $scope.$apply();

            if (self.selectedThread.id == conversation_id) {
                scrollBottom();
            }

        }
    }

})
();
