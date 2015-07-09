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

  MonitorController.$inject = ['$window', '$location', '$scope', '$mdSidenav', '$mdUtil', 'Monitor', '$filter', '$routeParams', '$sce'];

  /**
  * @namespace MonitorController
  */
  function MonitorController($window, $location, $scope, $mdSidenav,  $mdUtil, Monitor, $filter, $routeParams, $sce) {
    var vm = $scope;
    vm.moduleId = $routeParams.moduleId;
    vm.projectName = "";
    vm.taskName = "";
    vm.objects = [];

    Monitor.getTaskWorkerResults(vm.moduleId).then(function(data) {
      var task = data[0];
      var taskworkers = task.task_workers;
      for(var i = 0; i < taskworkers.length; i++) {
        var worker_alias = taskworkers[i].worker_alias;
        var taskworkerresults = taskworkers[i].task_worker_results;
        for(var j = 0; j < taskworkerresults.length; j++) {
          var template_item = taskworkerresults[j].template_item;
          var result = taskworkerresults[j].result;
          var status = taskworkerresults[j].status;
          var last_updated = taskworkerresults[j].last_updated;
          var obj = {
            worker_alias: worker_alias,
            template_item: template_item,
            result: result,
            status: status,
            last_updated: last_updated
          };
          vm.objects.push(obj);
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
      status |= 1;
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
        id: obj.twr.id,
        status: newStatus,
        created_timestamp: obj.twr.created_timestamp,
        last_updated: obj.twr.last_updated,
        task_worker: obj.twr.task_worker,
        template_item: obj.twr.template_item,
        result: obj.twr.result
      };
      Monitor.updateResultStatus(twr).then(
        function success(data, status) {
          console.log(obj.twr.id);
          var obj_ids = vm.objects.map( function (obj) { return obj.twr.id } )
          var index = obj_ids.indexOf(obj.twr.id)
          vm.objects[index].twr.status = newStatus;
        },
        function error(data, status) {
          console.log("Update failed!");
        }
      );
    }

    function downloadResults(objects) {
      var arr = [['status', 'submission', 'worker']];
      for(var i = 0; i < objects.length; i++) {
        var obj = objects[i];
        var temp = [getStatusName(obj.status), obj.submission, obj.worker_alias];
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