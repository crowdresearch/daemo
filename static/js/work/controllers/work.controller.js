//__author__ = 'lucamatsumoto'

(function () {
  'use strict';

	angular
	    .module('crowdsource.work.controllers', ['ngAnimate', 'ngSanitize', 'mgcrea.ngStrap', 'ngFileUpload'])
        .filter('bytes', function() {
            return function(bytes, precision) {
                if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '-';
                if (typeof precision === 'undefined') precision = 1;
                var units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'],
                    number = Math.floor(Math.log(bytes) / Math.log(1024));
                return (bytes / Math.pow(1024, Math.floor(number))).toFixed(precision) +  ' ' + units[number];
            }
        })
	    .controller('macroWorkSubmitController', macroWorkSubmitController);

	macroWorkSubmitController.$inject = ['$scope', '$modal', '$mdToast', '$http', '$timeout', 'Upload', 'WorkService'];

    function macroWorkSubmitController($scope, $modal, $mdToast, $http, $timeout, Upload, WorkService) { 
        $scope.displayedCollection = [];
        $scope.rowCollection=[];
            
        $scope.removeRow = function removeRow(row) {
            var index = $scope.rowCollection.indexOf(row);
            if (index !== -1) {
                WorkService.removeFile(row.id)
                $scope.rowCollection.splice(index, 1);
            }
        }

        $scope.taskInfo = "Task information will be displayed here...";

        $scope.$watch('files_to_upload', function () {
            $scope.upload($scope.files_to_upload);
        });

        $scope.upload = function (files) {
            if (files && files.length) {
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];
                    Upload.upload({
                        url: '/api/requesterinputfile/create',
                        file: file
                    }).progress(function (evt) {
                        var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
                        console.log('progress: ' + progressPercentage + '% ' + evt.config.file.name);
                    }).success(function (data, status, headers, config) {
                        // $mdToast.showSimple('file ' + config.file.name + 'uploaded. Response: ' + data);
                        console.log('file ' + config.file.name + 'uploaded. Response: ' +  JSON.stringify(data));
                        $scope.rowCollection.push({ name: config.file.name, size: config.file.size, timestamp: new Date(), id: data});
                    }).error(function(data, status, headers, config) {
                        $mdToast.showSimple('Error uploading ' + config.file.name);
                    });
                }
            }
        };
      }
})();