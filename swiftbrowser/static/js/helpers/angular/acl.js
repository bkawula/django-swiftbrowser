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

    // Update new inputs
    $scope.add_read_user();
    $scope.add_write_user();
    $scope.add_read_referrer();

    //Concat acls
    var read = $scope.concat_read_acl();
    var write = $scope.concat_write_acl();

    console.log(read);
    console.log(write);

    $http({
      method  : "POST",
      url     : baseurl + 'set_acls/' + $scope.container + "/",
      data    : $.param(
        {
          "read_acl": read,
          "write_acl": write,
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
          $scope.getACLs($scope.container);
        }
      );
  };

  /*
    Add new user to the read acl.
  */
  $scope.add_read_user = function () {
    if ($scope.read_new_user) {
      $scope.read_acl.users.push($scope.read_new_user);
      $scope.read_new_user = "";
    }
  };

  /* Remove the given index from the read user list. */
  $scope.remove_read_user = function (index) {
    $scope.read_acl.users.splice(index, 1);
  };

  /* Remove the given index from the read referrer list. */
  $scope.remove_read_referrer = function (index) {
    $scope.read_acl.referrers.splice(index, 1);
  };

  /*
    Add new user to the write acl.
  */
  $scope.add_write_user = function () {
    if ($scope.write_new_user) {
      $scope.write_acl.users.push($scope.write_new_user);
      $scope.write_new_user = "";
    }
  };

  /*
    Add new referrer to the read acl.
  */
  $scope.add_read_referrer = function () {
    if ($scope.read_new_referrer) {
      $scope.read_acl.referrers.push($scope.read_new_referrer);
      $scope.read_new_referrer = "";
    }
  };

  /* Remove the given index from the read user list. */
  $scope.remove_write_user = function (index) {
    $scope.write_acl.users.splice(index, 1);
  };

  /*
    Concatenate and return the read ACL
  */
  $scope.concat_read_acl = function () {
    var acl = "";
    var i;

    for (i = 0; i < $scope.read_acl.users.length; i++) {
      acl += $scope.read_acl.users[i] + ",";
    }

    for (i = 0; i < $scope.read_acl.referrers.length; i++) {
      acl += ".r:" + $scope.read_acl.referrers[i] + ",";
    }

    if ($scope.read_acl["public"]) {
      acl += ".r:*,";
    }
    if ($scope.read_acl.rlistings) {
      acl += ".rlistings";
    }

    acl = acl.replace(/(,$)/g, "");

    return acl;
  };

  /*
    Concatenate and return the write ACL
  */
  $scope.concat_write_acl = function () {
    var acl = "";
    var i;

    for (i = 0; i < $scope.write_acl.users.length; i++) {
      acl += $scope.write_acl.users[i] + ",";
    }

    acl = acl.replace(/(,$)/g, "");

    return acl;
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
