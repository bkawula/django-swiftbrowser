/*
  This file is used in acl.html.
  The controls the angular logic for mangaing ACLs.
*/
var app = angular.module('acl', ['messages']);

app.controller('AclCtrl', function ($scope, $http, baseurl, MessagesHandler) {

  /*jshint strict: false */
  $scope.container = ''; /*  The container who's ACL will be edited. */
  /* The base url of swiftbrowser, switbrowser is not always served from the
  root of the domain. */
  $scope.baseurl = baseurl;
  $scope.read_acl = ''; /* The read ACL for the container. */
  $scope.write_acl = ''; /* The write ACL for the container. */

  /* External function to set the container to operate on. */
  function setContainerName(container) {
    $scope.container = container;
    $scope.getACLs(container);
  }
  $scope.setContainerName = setContainerName;

  /* Get the current read and write ACLs */
  $scope.getACLs = function (container) {
    $http.get(baseurl + 'get_acls/' + container + "/").then(
      function (response) {
        $scope.read_acl = response.data.read_acl;
        $scope.write_acl = response.data.write_acl;
      }
    );
  };

  /* Set the ACLs */
  $scope.setACLs = function () {

    // Update new inputs
    $scope.add_read_user();
    $scope.add_write_user();
    $scope.add_read_referrer();

    //Concatenate ACLs
    var read = $scope.build_read_acl_string();
    var write = $scope.build_write_acl_string();

    // Submit a post to swift to set the ACLs
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

          //Update the ACLs
          $scope.getACLs($scope.container);
        }
      );
  };

  /*
    Add read_new_user to the read_acl list and clear it.
  */
  $scope.add_read_user = function () {
    if ($scope.read_new_user) {
      $scope.read_acl.users.push($scope.read_new_user);
      $scope.read_new_user = "";
    }
  };

  /* Remove the user at the given index from the read_acl list. */
  $scope.remove_read_user = function (index) {
    $scope.read_acl.users.splice(index, 1);
  };

  /* Remove the given index from the read_acl referrers list. */
  $scope.remove_read_referrer = function (index) {
    $scope.read_acl.referrers.splice(index, 1);
  };

  /* Add write_new_user to the write_acl list and clear it. */
  $scope.add_write_user = function () {
    if ($scope.write_new_user) {
      $scope.write_acl.users.push($scope.write_new_user);
      $scope.write_new_user = "";
    }
  };

  /* Add read_new_referrer to the read_acl referrers list. */
  $scope.add_read_referrer = function () {
    if ($scope.read_new_referrer) {
      $scope.read_acl.referrers.push($scope.read_new_referrer);
      $scope.read_new_referrer = "";
    }
  };

  /* Remove the given index from the write_acl list. */
  $scope.remove_write_user = function (index) {
    $scope.write_acl.users.splice(index, 1);
  };

  /* Build and return the read ACL string for swift by concatenating read
  users, referrers, public and rlistings.*/
  $scope.build_read_acl_string = function () {
    var acl = "";
    var i;

    // Concatenate all the read users
    for (i = 0; i < $scope.read_acl.users.length; i++) {
      acl += $scope.read_acl.users[i] + ",";
    }

    // Concatenante the referrers
    for (i = 0; i < $scope.read_acl.referrers.length; i++) {
      acl += ".r:" + $scope.read_acl.referrers[i] + ",";
    }

    /* If public is set, concat the swift string ".r:*" which makes the
    container public */
    if ($scope.read_acl.public) {
      acl += ".r:*,";
    }

    /* If rlistings set, concat the swift string ".rlistings" which makes the
    listing of the container public. */
    if ($scope.read_acl.rlistings) {
      acl += ".rlistings";
    }

    // Drop the trailing comma
    acl = acl.replace(/(,$)/g, "");

    return acl;
  };

  /* Build the write acl string for swift by concatenating the write users. */
  $scope.build_write_acl_string = function () {
    var acl = "";
    var i;

    // Concatenate the write users
    for (i = 0; i < $scope.write_acl.users.length; i++) {
      acl += $scope.write_acl.users[i] + ",";
    }

    // Drop the trailing comma
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
