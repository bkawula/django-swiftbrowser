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

  /*
    Add new user to the read acl.
  */
  $scope.add_read_user = function (user) {
    $scope.read_acl.users.push(user);
    $scope.read_new_user = "";
  };

  /*
    Add new user to the write acl.
  */
  $scope.add_write_user = function (user) {
    $scope.write_acl.users.push(user);
    $scope.write_new_user = "";
  };

  /*
    Add new referrer to the read acl.
  */
  $scope.add_read_referrer = function (referrer) {
    $scope.read_acl.referrers.push(referrer);
    $scope.read_new_referrer = "";
  };

  /*
    Add new referrer to the write acl.
  */
  $scope.add_write_referrer = function (referrer) {
    $scope.write_acl.referrers.push(referrer);
    $scope.write_new_referrer = "";
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
