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

        self.loading = true;
        self.conversations = [];

        self.getIcon = getIcon;
        self.toggle = toggle;
        self.sendMessage = sendMessage;
        self.closeConversation = closeConversation;

        var STATUS = {
            OPEN: 1,
            MINIMIZED: 2,
            CLOSED: 3,
            MUTED: 4
        };

        activate();

        function activate() {
            initiateOpenConversations();

            registerConversationHandler();
            registerMessageHandler();
        }

        function initiateOpenConversations() {
            if (!Message.conversations) {
                Message.listOpenConversations().then(
                    function success(data) {
                        Message.conversations = _.map(data[0], function (chat) {
                            var conversation = chat.conversation;
                            conversation.status = chat.status;
                            conversation.status_id = chat.id;
                            conversation.unread_count = 0;
                            return conversation;
                        });
                    },
                    function error(response) {
                        Message.conversations = [];
                    }).finally(function () {
                        self.conversations = Message.conversations;

                        // set status of each overlay
                        _.each(self.conversations, function (conversation) {
                            toggle(conversation.status == 1, null, conversation);
                        })
                    }
                );
            } else {
                self.conversations = Message.conversations;
            }
        }

        function registerConversationHandler() {
            $scope.$on('conversation', function (event, requester) {
                handleNewConversation(requester, true);
            });
        }

        function registerMessageHandler() {
            $scope.$on('message', function (event, data) {
                handleNewMessage(data);
            });
        }

        function handleNewConversation(requester, isExpanded) {
            // verify if conversation is already open for requester
            var conversation = _.find(self.conversations, function (conversation) {
                return conversation.recipient_names.indexOf(requester) >= 0;
            });

            // else make it
            if (conversation == null) {
                createConversation(requester, null, isExpanded);
            } else {
                if (isExpanded) {
                    toggle(isExpanded, null, conversation);
                }
            }
        }

        function handleNewMessage(message) {
            var user = message.sender;

            // verify if conversation is already open for requester
            var index = _.findIndex(self.conversations, function (conversation) {
                return conversation.recipient_names.indexOf(user) >= 0;
            });

            // if not, open it and make it currently active
            if (index < 0) {
                createConversation(user, message, true);
            } else {
                var conversation = self.conversations[index];

                // push the message to the conversation
                angular.extend(message, {is_self: false});

                if (!conversation.hasOwnProperty('messages')) {
                    listMessages(conversation);
                } else {
                    $scope.$apply(function () {
                        pushMessage(message, conversation);
                    });
                }
            }
        }

        function createConversation(user_alias, message, shouldExpand) {
            //console.log("createConversation");

            User.getProfile(user_alias).then(function (response) {
                var user = {
                    user_id: response[0].user,
                    alias: user_alias
                };

                Message.createConversation([user.user_id], null).then(
                    function success(data) {
                        self.conversations.push(data[0]);
                        var position = self.conversations.length - 1;
                        var conversation = self.conversations[position];

                        if (shouldExpand) {
                            toggle(shouldExpand, null, conversation);
                        }
                    },
                    function error(data) {
                    }).finally(function () {

                    }
                );
            });
        }

        // assumes conversation and message are all set by now
        function pushMessage(message, conversation) {
            //console.log("pushMessage");

            if(conversation.isExpanded){
                conversation.unread_count = 0;
            }else{
                conversation.unread_count++;
            }

            conversation.messages.push(message);
            scrollBottom(conversation);
        }

        function getIcon(conversation) {
            return conversation.isExpanded ? 'close' : '';
        }

        function toggle(open, e, conversation) {
            //console.log("toggle");

            conversation.isExpanded = (open != null) ? open : !conversation.isExpanded;

            if (e && $(e.target).hasClass('_toggle'))
                return;

            if (conversation.isExpanded) {
                listMessages(conversation);
            } else {
                scrollBottom(conversation);
            }

            var status = conversation.isExpanded ? STATUS.OPEN : STATUS.MINIMIZED;
            updateConversation(status, conversation);
        }

        function updateConversation(status, conversation) {
            if (!conversation) return;

            Message.updateConversationStatus(conversation, status).then(
                function success(data) {
                    conversation.status = status;

                    if (status == STATUS.CLOSED) {
                        var index = self.conversations.indexOf(conversation);
                        self.conversations.splice(index, 1);
                    }
                },
                function error(data) {
                }).finally(function () {

                }
            );
        }


        function listMessages(conversation) {
            //console.log("listMessages");

            if(conversation.isExpanded){
                conversation.unread_count = 0;
            }else{
                conversation.unread_count++;
            }

            if (!conversation.hasOwnProperty('messages')) {
                self.loading = true;

                Message.listMessages(conversation.id).then(
                    function success(data) {
                        angular.extend(conversation, {messages: data[0]});
                        self.loading = false;
                    },
                    function error(data) {
                    }).finally(function () {
                        scrollBottom(conversation);
                    }
                );
            } else {
                scrollBottom(conversation);
            }
        }


        function sendMessage(conversation) {
            Message.sendMessage(conversation.newMessage, conversation.recipient_names[0],
                conversation.id).then(
                function success(data) {

                    var conversation = _.find(self.conversations, function (obj) {
                        return obj.id == data[0].conversation;
                    });

                    if (!conversation.hasOwnProperty('messages')) {
                        angular.extend(conversation, {'messages': []});
                    }

                    conversation.messages.push(data[0]);
                    conversation.newMessage = null;
                    scrollBottom(conversation);
                },
                function error(data) {
                }).finally(function () {

                }
            );
        }

        function scrollBottom(conversation) {
            $timeout(function () {
                var messageDiv = $('._c' + conversation.id + ' > ._overlay-messages');
                messageDiv.animate({scrollTop: messageDiv[0].scrollHeight}, 1000, 'swing');
            }, 10, false);
        }

        function closeConversation(e, conversation) {
            e.preventDefault();
            updateConversation(STATUS.CLOSED, conversation);
        }
    }

})
();
