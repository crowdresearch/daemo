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
    vm.projectName = $routeParams.project;
    vm.moduleName = $routeParams.milestone;

    vm.entries = [];
    vm.data_keys = [];
    vm.data_arr = [];
    Monitor.getMonitoringData(vm.moduleId).then(function(data){
      var tasks = data[0];
      vm.data_keys = Object.keys(JSON.parse(tasks[0].data));
      for(var i = 1; i <= vm.data_keys.length; i++) {
        vm.data_arr.push(i);
      }
      for(var i = 0; i < tasks.length; i++){
        var task_workers = tasks[i].task_workers;
        for(var j = 0; j < task_workers.length; j++) { 
          var task_worker_results = task_workers[j].task_worker_results;
          var data_source_results = {};
          for(var k = 0; k < task_worker_results.length; k++) {
            //This check should be unnecessary because i dont think we should create
            //taskworkerresults for template_items that dont accept input...but just in case for now
            if(task_worker_results[k].template_item.role !== 'input') continue;
            var data_source = task_worker_results[k].template_item.data_source;
            var result = task_worker_results[k].result;
            data_source_results[data_source] = result;
          }
          var entry = {
            id: task_workers[j].id,
            data: JSON.parse(tasks[i].data),
            worker_alias: task_workers[j].worker_alias,
            status: task_workers[j].status,
            results: data_source_results
          };
          vm.entries.push(entry);
        }
      }
    });

    vm.filter = undefined;
    vm.order = undefined;
    vm.inprogress = 1;
    vm.submitted = 2;
    vm.accepted = 3;
    vm.returned = 4;

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
      return status == 1 ? 'in progress' : (status == 2 ? 'submitted' : (status == 3 ? 'accepted' : 'returned'));
    }

    function getStatusColor (status) {
      return status == 3 ? 'gray' : (status == 2 ? 'dark' : 'green');
    }

    function getAction (status) {
      return status == 2;
    }

    function updateResultStatus(entry, newStatus) {
      var taskworker = {
        id: entry.id,
        status: newStatus,
      };
      Monitor.updateResultStatus(taskworker).then(
        function success(data, status) {
          var entry_ids = vm.entries.map( function (entry) { return entry.id } )
          var index = entry_ids.indexOf(entry.id)
          vm.entries[index].status = newStatus;
        },
        function error(data, status) {
          console.log("Update failed!");
        }
      );
    }

    function downloadResults() {
      Monitor.getResultsFile(vm.moduleId, vm.moduleName, vm.projectName).then(
        function success(data, status) {
          console.log("yeeee");
        },
        function error(data, status) {
          console.log("Download failed!");
        }
      );
    }

    // function downloadResults(entries) {
    //   var columnHeaders = ['created', 'last_updated', 'status', 'worker']
    //   for(var i = 0; i < vm.data_keys.length; i++) {
    //     columnHeaders.push(vm.data_keys[i]);
    //   }
    //   for(var i = 0; i < vm.data_arr.length; i++) {
    //     columnHeaders.push("Output_" + vm.data_arr[i]);
    //   }
    //   var arr = [[columnHeaders]];
    //   for(var i = 0; i < entries.length; i++) {
    //     var entry = entries[i];
    //     var temp = [entry.created, entry.last_updated, getStatusName(entry.status), entry.worker_alias];
    //     for(var j = 0; j < vm.data_keys.length; j++) {
    //       temp.push(entry.data[vm.data_keys[j]]);
    //     }
    //     for(var j = 0; j < vm.data_keys.length; j++) {
    //       temp.push(entry.results[vm.data_keys[j]]);
    //     }
    //     arr.push(temp);
    //   }
    //   var csvArr = [];
    //   for(var i = 0, l = arr.length; i < l; ++i) {
    //     csvArr.push(arr[i].join(','));
    //   }

    //   var csvString = csvArr.join("%0A");
    //   var a         = document.createElement('a');
    //   a.href        = 'data:text/csv;charset=utf-8,' + csvString;
    //   a.target      = '_blank';
    //   a.download    = vm.projectName.replace(/\s/g,'') + '_' + vm.moduleName.replace(/\s/g,'') + '_data.csv';

    //   document.body.appendChild(a);
    //   a.click();
    // }

  }
})();