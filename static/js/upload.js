function checklang() {
  var value = document.getElementById("lang").value
  document.getElementById("submit").disabled = (value == "")
}
function checkSubmit(form) {
  form.submit.disabled = true;
  return true;
}
