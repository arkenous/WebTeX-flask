$(window).load(init());

function init() {
  $(".ldap").hide();
  readConfig();

  $("input[name='mode']:radio").change(function() {
    if ($(this).val() == 'local') {
      $(".ldap").hide("normal");
    } else {
      $(".ldap").show("normal");
    }
  });
  $("#OK").click(function (event) {
    event.preventDefault();
    saveConfig();
  });
}


function readConfig() {
  $.ajax({
    type: 'POST',
    url: '/readConfig',
    contentType: 'application/json',
    success: function(data) {
      var parsed = JSON.parse(data.ResultSet);
      var result = parsed.result;
      if (result == "Success") {
        $("input[name='mode']:radio").val(parsed.mode);
        $("#ldap_address").val(parsed.ldap_address);
        $("#ldap_port").val(parsed.ldap_port);
        $("#ldap_basedn").val(parsed.ldap_basedn);
        $("#java_home").val(parsed.java_home);
        $("#redpen_path").val(parsed.redpen_conf_path);
      }
    }
  });
  return false;
}


function saveConfig() {
  var mode = $("input[name='mode']:radio").val();

  var ldap_address = $("#ldap_address").val();
  var ldap_port = $("#ldap_port").val();
  var ldap_basedn = $("#ldap_basedn").val();

  var java_home = $("#java_home").val();
  var redpen_conf_path = $("#redpen_path").val();

  var json = JSON.stringify({
    "mode": mode,
    "ldap_address": ldap_address,
    "ldap_port": ldap_port,
    "ldap_basedn": ldap_basedn,
    "java_home": java_home,
    "redpen_conf_path": redpen_conf_path
  });

  $.ajax({
    type: 'POST',
    url: '/saveConfig',
    data: json,
    contentType: 'application/json',
    success: function() {
      console.log("save config succeed");
      $(location).attr("href", "/login");
    }
  });
  return false;
}