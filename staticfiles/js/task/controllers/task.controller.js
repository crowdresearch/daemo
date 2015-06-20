/**
* TaskController
* @namespace crowdsource.task.controllers
 * @author ryosuzuki
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.task.controllers')
    .controller('TaskController', TaskController);

  TaskController.$inject = ['$scope', 'Task'];

  /**
  * @namespace TaskController
  */
  function TaskController($scope, Task) {
    var vm = $scope;

    vm.currentStep = 1;
    vm.advancedOption = false;
    vm.categories = [];
    vm.task = {
      date: new Date()
    }
    vm.getCategories = Task.getCategories;
    vm.selectCategory = selectCategory;
    vm.showStep = showStep;


    vm.categories = vm.getCategories();

    function showStep (step) {
      vm.currentStep = step;
    }

    function selectCategory (category) {
      vm.task.category = category;
    }

    function showResult ($event) {
      $event.preventDefault();
      alert(JSON.stringify(vm.task));
    }

  }
})();