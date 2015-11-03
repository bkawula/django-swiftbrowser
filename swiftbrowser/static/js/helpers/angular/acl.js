var app = angular.module('acl', []);

app.controller('AclCtrl', function ($scope, $http) {

  function setContainerName(container) {
    console.log(container);
  }
  $scope.setContainerName = setContainerName;

  // Provides containerview.js access to this function
  $scope.$on("setContainerName", function (container) {
    setContainerName(container);
  });

});


/* Added in for CSRF support. */
app.config(function ($httpProvider) {
  $httpProvider.defaults.headers.post['X-CSRFToken'] = $('input[name=csrfmiddlewaretoken]').val();
});
