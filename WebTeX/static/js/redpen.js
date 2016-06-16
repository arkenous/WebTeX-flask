var editor;

$(window).load(init());
$(window).resize(resizeAce);

function init() {
  editor = ace.edit("editor");
  resizeAce();

  $("#correct").click(function() {
    correctDoc();
  });
}

function resizeAce() {
  editor.resize(true);
}

function correctDoc() {
  editor.setReadOnly(true);
  var text = editor.getValue();
  var json = JSON.stringify({"text": text});

  $.ajax({
    type: 'POST',
    url: '/correct',
    data: json,
    contentType: 'application/json',
    success: function (data) {
      var result = JSON.parse(data.ResultSet).result;
      if (result === 'Success') {
        var redpenLog = JSON.parse(data.ResultSet).redpenout;
        $("#result").empty();
        for (i = 0; i < redpenLog.length; i++) {
          $("#result").append(redpenLog[i] + "<br/>");
        }
      }
    }
  });

  editor.setReadOnly(false);
  return false;
}

