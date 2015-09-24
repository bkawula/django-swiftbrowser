/*
  Prompt the user twice to confirm th deletion of a folder.
*/
/*global confirm: true */
function double_confirm() {
  var confirm1 = confirm('Delete folder?');
  if (confirm1) {
    var confirm2 = confirm('Deleting this folder will delete everything in the folder. Are you sure?');
    if (confirm2) {
      return true;
    }
  }
  return false;
}
