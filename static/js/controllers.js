function TodoListCtl($scope, TodoList){

$scope.todo_items = []

TodoList.query(function(response){
    $scope.todo_items = response;
});

$scope.createTodoItem = function () {
    var todo_item = new TodoList();
    todo_item.description = $scope.todo_list_name;
    todo_item.$save(function(response){
        $scope.todo_items.push(response);
    });
};

$scope.deleteTodoItem = function(todo_item){
    todo_item.$delete(function(response){
        var index = $scope.todo_items.indexOf(todo_item);
        $scope.todo_items.splice(index, 1);
    });
};

$scope.toggleTodoItemStatus = function(todo_item) {
    TodoList.update({'id': todo_item.id, 'description': todo_item.description, 'done': todo_item.done});
};

}