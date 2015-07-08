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

  MonitorController.$inject = ['$window', '$location', '$scope', '$mdSidenav', '$mdUtil', 'Monitor', '$filter'];

  /**
  * @namespace MonitorController
  */
  function MonitorController($window, $location, $scope, $mdSidenav,  $mdUtil, Monitor, $filter) {
    var vm = $scope;
    vm.workers = [];
    Monitor.getTaskWorkerResults().then(function(data) {
      vm.workers = data[0];
    });
    vm.filter = undefined;
    vm.order = undefined;
    vm.inprogress = 1;
    vm.submitted = 2;
    vm.approved = 3;
    vm.rejected = 4;

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

    function toggleRight (worker) {
      vm.worker = worker
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

    function getPercent (workers, status) {
      status |= 1;
      var complete = workers.filter( function (worker) {
        return worker.status == status;
      });
      return Math.round((complete.length / workers.length) * 100);
    }

    function showModal (worker) {
      vm.selectedWorker = worker;
      $('#myModal').modal();
    }

    function getStatusName (status) {
      return status == 1 ? 'in progress' : (status == 2 ? 'submitted' : (status == 3 ? 'approved' : 'rejected'));
    }

    function getStatusColor (status) {
      return status == 3 ? 'gray' : (status == 2 ? 'dark' : 'green');
    }

    function getAction (status) {
      return status == 2;
    }

    function updateResultStatus(worker, newStatus) {
      var twr = {
        id: worker.id,
        status: newStatus,
        created_timestamp: worker.created_timestamp,
        last_updated: worker.last_updated,
        task_worker: worker.task_worker,
        template_item: worker.template_item,
        result: worker.result
      };
      Monitor.updateResultStatus(twr).then(
        function success(data, status) {
          window.location.reload();
        },
        function error(data, status) {
          console.log("Update failed!");
        }
      );
    }

    function downloadResults(workers) {
      var arr = [['status', 'submission', 'worker']];
      for(var i = 0; i < workers.length; i++) {
        var worker = workers[i];
        var temp = [getStatusName(worker.status), worker.created_timestamp, worker.task_worker.worker.profile.worker_alias];
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