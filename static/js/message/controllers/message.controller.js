/**
 * MessageController
 * @namespace crowdsource.message.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.message.controllers')
        .controller('MessageController', MessageController);

    MessageController.$inject = ['Message', '$websocket', '$rootScope', '$routeParams', '$scope', '$location', 'User', '$filter'];

    /**
     * @namespace MessageController
     */
    function MessageController(Message, $websocket, $rootScope, $routeParams, $scope, $location, User, $filter) {

        var self = this;
        self.loading = false;
        self.selectedThread = null;
        self.messages = [];
        self.users = [];
        self.conversations = [];
        self.sendMessage = sendMessage;
        self.newMessage = null;
        self.createNew = createNew;
        self.querySearch = querySearch;
        self.selectedItemChange = selectedItemChange;
        self.searchTextChange = searchTextChange;
        self.transformChip = transformChip;
        self.newRecipients = [];
        self.startConversation = startConversation;
        self.newConversation = null;
        self.getNewConversationText = getNewConversationText;
        self.setSelected = setSelected;
        self.isSelected = isSelected;
        self.isInputDisabled = isInputDisabled;
        self.cancelNewConversation = cancelNewConversation;
        activate();

        function activate() {
            initializeWebSocket();
            listConversations();
        }

        function setUser(username) {
            $location.search('t', username)
        }

        function listConversations() {
            Message.listConversations().then(
                function success(data) {
                    self.conversations = data[0];
                    if (self.conversations.length) {
                        var user = $location.search()['t'];
                        var conversation = $filter('filter')(self.conversations, function (obj) {
                            return obj.recipient_names[0] == user;
                        });
                        if (!user || !conversation.length) {
                            setUser(self.conversations[0].recipient_names[0]);
                            self.selectedThread = self.conversations[0];

                        }
                        else {
                            self.selectedThread = conversation[0];
                        }

                        listMessages(self.selectedThread.id);

                    }
                },
                function error(data) {
                }).finally(function () {

                }
            );
        }

        function listMessages(conversation_id) {
            Message.listMessages(conversation_id).then(
                function success(data) {
                    self.selectedThread.messages = data[0];
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

        function newMessage() {
            Message.sendMessage(self.newMessage, self.selectedThread.recipient_names[0], self.selectedThread.id).then(
                function success(data) {
                    if (!self.selectedThread.hasOwnProperty('messages'))
                        angular.extend(self.selectedThread, {'messages': []});
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

        function initializeWebSocket() {
            self.ws = $websocket.$new({
                url: $rootScope.getWebsocketUrl() + '/ws/inbox?subscribe-user',
                lazy: true,
                reconnect: true
            });
            self.ws
                .$on('$message', function (data) {
                    receiveMessage(data);
                })
                .$on('$close', function () {

                })
                .$on('$open', function () {

                })
                .$open();
        }

        function scrollBottom() {
            var messageDiv = $('._message-detail');
            messageDiv.scrollTop(messageDiv[0].scrollHeight);
        }

        function createNew() {
            $location.path('/m/');

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


        function receiveMessage(data) {
            var message = JSON.parse(data);
            angular.extend(message, {is_self: false});
            var conversation = $filter('filter')(self.conversations, {id: message.conversation});
            var conversation_id = null;
            if (conversation.length) {
                conversation[0].messages.push(message);
                conversation[0].last_message.body = message.body;
                conversation_id = conversation[0].id;
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
