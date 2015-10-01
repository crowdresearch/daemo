/**
* MonitorController
* @namespace crowdsource.monitor.controllers
 * @author ryosuzuki
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.monitor.controllers')
    .controller('MonitorController', MonitorController);

  MonitorController.$inject = ['$window', '$location', '$scope', '$mdSidenav', '$mdToast', '$mdUtil', 'Monitor', '$filter', '$routeParams', '$sce'];

  /**
  * @namespace MonitorController
  */
  function MonitorController($window, $location, $scope, $mdSidenav, $mdToast,  $mdUtil, Monitor, $filter, $routeParams, $sce) {
    var vm = $scope;
    vm.projectId = $routeParams.projectId;
    vm.objects = [];
    vm.projectName = "";

    Monitor.getProject(vm.projectId).then(function(data){
      vm.project = data[0];
      vm.projectName = vm.project.name;
      vm.modules = vm.project.modules;
      for(var i = 0; i < vm.modules.length; i++) {
        var projectModule = vm.modules[i];
        for(var j = 0; j < projectModule.module_tasks.length; j++){
          var task = projectModule.module_tasks[j];
          var taskworkers = task.task_workers;
          for(var k = 0; k < taskworkers.length; k++) {
            var worker_alias = taskworkers[k].worker_alias;
            var taskworkerresults = taskworkers[k].task_worker_results;
            var obj = {
              id: taskworkers[k].worker,
              worker_alias: worker_alias,
              result: taskworkerresults,
              milestone: projectModule.name,
              status: status || 1,
              last_updated: taskworkers[k].last_updated
            };
            vm.objects.push(obj);
          }
        }
      }
    });

    vm.filter = undefined;
    vm.order = undefined;
    vm.created = 1;
    vm.accepted = 2;
    vm.rejected = 3;

    vm.showModal = showModal;
    vm.getPercent = getPercent;
    vm.orderTable = orderTable;
    vm.selectStatus = selectStatus;
    vm.getStatusName = getStatusName;
    vm.getStatusColor = getStatusColor;
    vm.getAction = getAction;
    vm.updateResultStatus = updateResultStatus;
    vm.downloadResults = downloadResults;

    vm.toggleRight = toggleRight();
    vm.updateCurrObject = updateCurrObject;

    vm.currObject;
    function updateCurrObject(obj) {
      vm.currObject = obj;
      vm.currObject.source_url = $sce.trustAsResourceUrl(obj.template_item.data_source);
    } 

    function toggleRight () {
      var debounceFn =  $mdUtil.debounce(function(){
        $mdSidenav('right')
        .toggle()
      },30);
      return debounceFn;
    }

    vm.close = function () {
      $mdSidenav('right').close();
    };

    function selectStatus (status) {
      vm.filter = vm.filter !== status ? status : undefined ;
    }

    function orderTable (key) {
      vm.order = vm.order === key ? '-'+key : key;
    }

    function getPercent (objects, status) {
      var complete = objects.filter( function (obj) {
        return obj.status == status;
      });
      return Math.round((complete.length / objects.length) * 100);
    }

    function showModal (worker) {
      vm.selectedWorker = worker;
      $('#myModal').modal();
    }

    function getStatusName (status) {
      return status == 1 ? 'created' : (status == 2 ? 'accepted' : 'rejected');
    }

    function getStatusColor (status) {
      return status == 3 ? 'gray' : (status == 2 ? 'dark' : 'green');
    }

    function getAction (status) {
      return status == 2;
    }

    function updateResultStatus(obj, newStatus) {
      var twr = {
        id: obj.id,
        status: newStatus,
        created_timestamp: obj.created_timestamp,
        last_updated: obj.last_updated,
        template_item: obj.template_item,
        result: obj.result
      };
      Monitor.updateResultStatus(twr).then(
        function success(data) {
          var obj_ids = vm.objects.map( function (obj) { return obj.id } )
          var index = obj_ids.indexOf(obj.id)
          vm.objects[index].status = newStatus;
        },
        function error(data) {
          console.log("Update failed!");
          $mdToast.showSimple('Could not udpate result status.');
        }
      );
    }

    function downloadResults(objects) {
      var arr = [['status', 'last_updated', 'worker']];
      for(var i = 0; i < objects.length; i++) {
        var obj = objects[i];
        var temp = [getStatusName(obj.status), obj.last_updated, obj.worker_alias];
        arr.push(temp);
      }
      var csvArr = [];
      for(var i = 0, l = arr.length; i < l; ++i) {
        csvArr.push(arr[i].join(','));
      }

      var csvString = csvArr.join("%0A");
      var a         = document.createElement('a');
      a.href        = 'data:attachment/csv,' + csvString;
      a.target      = '_blank';
      a.download    = 'data.csv';

      document.body.appendChild(a);
      a.click();
    }

  }
})();