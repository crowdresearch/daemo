angular.module('todolistItemService', ['ngResource']).
    factory('TodoList', function($resource){
        return $resource('api/:todo_item_id', {todo_item_id: '@id'}, {
            save: {method: 'POST', isArray:false},
            query: {method: 'GET', isArray:true},
            update: {method: 'PUT', isArray:false},
            destroy: {method: 'DELETE', isArray:false}
        });
    });