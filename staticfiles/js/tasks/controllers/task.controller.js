//neilthemathguy @TODO add serverice
var rankingApp = angular.module('crowdsource.tasks.controllers', ['smart-table', 'ui.bootstrap']);

rankingApp.controller('taskController', function($scope, $log, $http) {
  $scope.displayedCollection = [];
  $scope.rowCollection=[];
  $http.get("/api/module/?format=json").success(function(data,config) {
    $scope.displayedCollection = data;
    $scope.rowCollection= data;
    console.log($scope.displayedCollection)
  }).error(function(data, status, headers, config) {
    console.log(status)
  });

  $scope.gridOptionsTask = {
    multiSelect: false,
    enablePinning: true,
    data:'task',
    columnDefs: [
      { field: "name", displayName: 'Name', width: 200, pinned: true },
      { field: "description", displayName: 'Description', width:150 },
      { field:"keywords",displayName: 'Keywords', width:190 },
      { field: "module_timeout", displayName:'Hours Remain', width:130 },
      { field: "repetition", displayName: 'Repetition', width: 100 },
      { field: "price", displayName: 'Pay', width: 60 },
    ]
  };

  var vm = $scope;
  vm.currentStep = 1;
  vm.advancedOption = false;

  vm.categories = [
    { id: 1, name: 'Programming', icon: 'fa-file-code-o'},
    { id: 2, name: 'Design',      icon: 'fa-magic'},
    { id: 3, name: 'Movies',      icon: 'fa-film'},
    { id: 4, name: 'Photos',      icon: 'fa-photo'},
    { id: 5, name: 'Accounting',  icon: 'fa-bar-chart'},
    { id: 6, name: 'Legal',       icon: 'fa-legal'},
    { id: 7, name: 'Translation', icon: 'fa-comments-o'},
    { id: 8, name: 'Writing',     icon: 'fa-file-word-o'},
  ];

  vm.task = {}
  /*
  vm.task = {
    category: vm.categories[0],
    name: 'FJWEOFJOWEJFOEJ',
    description: 'FJWOFJWOEJOFE'
  }
  */
  vm.task.date = new Date();

  vm.format = 'yyyy-MM-dd'
  vm.selectCategory = function (category) {
    vm.task.category = category;
  }

  vm.showResult = function ($event) {
    $event.preventDefault();
    alert(JSON.stringify(vm.task));
  }

  vm.showStep = function (step) {
    vm.currentStep = step;
  };

  vm.datePickerOpen = true;
  vm.toggleDatePicker = function($event) {
    $event.stopPropagation();
    vm.datePickerOpen = !vm.datePickerOpen;
  };


});

