var app = angular.module('acl', ['messages']);

app.controller('AclCtrl', function ($scope, $http, baseurl, MessagesHandler) {

  $scope.container = ''; /*  The container who's ACL will be edited. */
  $scope.baseurl = baseurl; /* The base url of swiftbrowser. */
  $scope.read_acl = ''; /* The read ACL for the container. */
  $scope.write_acl = ''; /* The write ACL for the container. */

  /*
    External function to set the container to operate on.
  */
  function setContainerName(container) {
    $scope.container = container;
    $scope.getACLs(container);
  }
  $scope.setContainerName = setContainerName;

  /*
    Get the current read and write ACLs
  */
  $scope.getACLs = function (container) {
    $http.get(baseurl + 'get_acls/' + container + "/").then(
      function (response) {
        $scope.read_acl = response.data.read_acl;
        $scope.write_acl = response.data.write_acl;
      }
    );
  };

  /*
    Set the ACLs
  */
  $scope.setACLs = function () {
    $http({
      method  : "POST",
      url     : baseurl + 'set_acls/' + $scope.container + "/",
      data    : $.param(
        {
          "read_acl": $scope.read_acl,
          "write_acl": $scope.write_acl,
          "csrfmiddlewaretoken": $('input[name=csrfmiddlewaretoken]').val()
        }
      ),  // pass in data as strings
      headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
      .success(
        function (response) {
          if (response.error) {
            MessagesHandler.newErrorMessage(response.error);
          } else {
            MessagesHandler.newSuccessMessage(response.success);
          }
        }
      );
  };
});


/* Added in for CSRF support. */
app.config(function ($httpProvider) {
  $httpProvider.defaults.headers.post['X-CSRFToken'] = $('input[name=csrfmiddlewaretoken]').val();
});

/*
  Obtain the base url of the application to make calls to the server.
*/
app.config(["$provide", function ($provide) {
  $provide.value("baseurl", $("#baseurl").attr("href"));
}]);