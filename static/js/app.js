'use strict'

angular.module('todo', ['todolistItemService']).config(function($httpProvider) {
    $httpProvider.defaults.headers.post  = {
        'X-CSRFToken': $.cookie('csrftoken'),
        'Content-Type': 'application/json'
    };
});