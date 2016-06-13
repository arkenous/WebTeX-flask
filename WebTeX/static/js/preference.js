$(window).load(init());

function init() {
  $("#ldap").hide("normal");

  $("#switch-ldap").change(function () {
    if ($(this).prop('checked')) {
      $("#ldap").show("normal");
    } else {
      $("#ldap").hide("normal");
    }
  });

  readConfig();


}

function readConfig() {
  $.ajax({
    type: 'POST',
    url: '/readConfig',
    contentType: 'application/json',
    success: function(data) {
      var parsed = JSON.parse(data.ResultSet);
      var result = parsed.result;
      if (result === "Success") {
        if (parsed.mode === 'ldap') {
          $("#switch-ldap").prop('checked', true);
        } else {
          $("#switch-ldap").prop('checked', false);
        }

        $("#ldap-address").val(parsed.ldap_address);
        $("#ldap-port").val(parsed.ldap_port);
        $("#ldap-basedn").val(parsed.ldap_basedn);

        $("#redpen-path").val(parsed.redpen_conf_path);
        $("#java-home").val(parsed.java_home);
      }
    }
  });
  return false;
}