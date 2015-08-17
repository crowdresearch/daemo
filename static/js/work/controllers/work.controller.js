
(function () {
  'use strict';

	angular
		.module('crowdsource.work.controllers', ['ngFileUpload', 'angular.filter'])
		.controller('MacroWorkSubmitController', MacroWorkSubmitController);

	MacroWorkSubmitController.$inject = ['$scope', '$mdToast', '$http', '$timeout', 'Upload', 'WorkService'];

	function MacroWorkSubmitController($scope, $mdToast, $http, $timeout, Upload, WorkService) {
		var vm = this;
		vm.filesToUpload = [];
		vm.uploadedFiles=[];
		vm.taskInfo = "Task information will be displayed here...";
		vm.commentText = "";

		// accepts multiple files to upload
		$scope.$watch(
			function () {
				return vm.filesToUpload;
			},
			function (newVal, oldVal) {
				// won't upload if the file is already uploaded
				if (newVal && newVal.length) {
					for (var i = 0; i < newVal.length; i++) {
						var file = newVal[i];

						var isNewFile = true;
						for (var j=0; j < vm.uploadedFiles.length; j++) {
							if (vm.uploadedFiles[j].name == file.name) {
								isNewFile = false;
								break;
							}
						}

						if (isNewFile) {
							vm.upload(file);
						}
					}
				}
			}
		);

		// upload single file via csvmanager
		vm.upload = function (file) {
			Upload.upload({
				url: '/api/csvmanager/create',
				file: file
			}).progress(function (evt) {
				var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
				console.log('progress: ' + progressPercentage + '% ' + evt.config.file.name);
			}).success(function (data, status, headers, config) {
				// $mdToast.showSimple('file ' + config.file.name + 'uploaded. Response: ' + data);
				console.log('file ' + config.file.name + 'uploaded. Response: ' +  JSON.stringify(data));
				vm.uploadedFiles.push({ name: config.file.name, size: config.file.size, timestamp: new Date(), id: data});
			}).error(function(data, status, headers, config) {
				$mdToast.showSimple('Error uploading ' + config.file.name);
			});
		};

		// remove uploaded file from the server and uploadedFiles
		vm.removeRow = function (row) {
			var index = vm.uploadedFiles.indexOf(row);
			if (index !== -1) {
				WorkService.removeFile(row.id);
				vm.uploadedFiles.splice(index, 1);
			}
		}

		// remove all files in uploadedFiles from the server
		vm.removeAll = function () {
			for (var i=0; i < vm.uploadedFiles.length; i++) {
				WorkService.removeFile(vm.uploadedFiles[i].id);
			}
			vm.uploadedFiles=[];
		}

		vm.cancel = function ($event) {
			vm.removeAll();
			$mdToast.showSimple('Cancelled: ' + vm.commentText);
		};

		vm.submit = function ($event) {
			var idList = [];
			for (var i=0; i < vm.uploadedFiles.length; i++) {
				idList.push(vm.uploadedFiles[i].id);
			}
			$mdToast.showSimple('Submitted RequesterInputFile[' + idList.join(',') + ']: ' + vm.commentText);
		};

	}
})();