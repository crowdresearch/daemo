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
                        var conversation = null;
                        var user = $location.search()['t'];
                        if (user.length) {
                            conversation = $filter('filter')(self.conversations, function (obj) {
                                return obj.recipient_names[0] == user;
                            })[0];
                        }
                        else {
                            setUser(self.conversations[0].recipient_names[0]);
                            conversation = self.conversations[0];
                        }
                        self.selectedThread = conversation;
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
                })
                .$open();
        }

        function scrollBottom() {
            var messageDiv = $('._task-submissions');
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

        function isSelected(conversation){
            return angular.equals(self.selectedThread, conversation);
        }
    }

})
();
