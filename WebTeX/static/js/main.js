var editor;
var cwd = "";

$(window).load(init());

function init() {
  editor = ace.edit("editor");
  readDirectory($("#username").text());

  $("#createDirectory").click(function () {
    createDirectory($('#directoryName').val());
  });

  $("#upload").click(function (event) {
    // ajaxでファイルのPOSTを行いたいので，formのデフォルトPOSTを行わせない
    event.preventDefault();
    upload();
  });

  $("#compile").click(function () {
    compile();
  });

  // Ctrl + Sでコンパイルさせたい
  document.onkeydown = function (e) {
    if (event.ctrlKey) {
      if (event.keyCode == 83) {
        //alert("Ctrl + S");
        compile();
        event.keyCode = 0;
        return false;
      }
    }
  }

  document.onkeypress = function (e) {
    if (e != null) {
      if ((e.ctrlKey || e.metaKey) && e.which == 115) {
        //alert("Ctrl + S");
        compile();
        return false;
      }
    }
  }
}


// 初回起動およびディレクトリ作成時に実行
function readDirectory() {
  $.ajax({
    type: 'POST',
    url: '/readDirectory',
    contentType: 'application/json',
    success: function (data) {
      $("#directorylist").empty();
      $("#directorylist").append(
          "<li><a data-toggle='modal' href='#createDirectoryModal'>Create directory</a></li>"
      );
      $("#directorylist").append(
          "<li class='divider' role='separator'></li>"
      );

      // data.ResultSetにPythonで作成したjsonが入る
      var directoryList = JSON.parse(data.ResultSet).name;

      for (i = 0; i < directoryList.length; i++) {
        $("#directorylist").append(
            "<li><a href='#' class='directoryItem' value='" + directoryList[i] + "'>" + directoryList[i] + "</a></li>"
        );
      }

      $("a.directoryItem").click(function () {
        setDirectory($(this).attr("value"));
      });
    }
  });
  return false;
}


function createDirectory(directoryName) {
  // スクリプトに渡すJSONを作成
  var json = JSON.stringify({"name": directoryName});

  $.ajax({
    type: 'POST',
    url: '/createDirectory',
    data: json,
    contentType: 'application/json',
    success: function () {
      readDirectory();
    }
  });
  return false;
}


function setDirectory(directoryItem) {
  var json = JSON.stringify({"name": directoryItem});

  $.ajax({
    type: 'POST',
    url: '/setDirectory',
    data: json,
    contentType: 'application/json',
    success: function (data) {
      var result = JSON.parse(data.ResultSet).result;
      if (result == "Success") {
        cwd = directoryItem;
        readFilelist(directoryItem);

        // document.texファイルが存在するなら，読み込む
        var exist = JSON.parse(data.ResultSet).exist;
        if (exist == "True") {
          var text = JSON.parse(data.ResultSet).text;
          editor.setValue(text);
        }
      } else {
        alert("Set Directory Failure");
      }
    }
  });
  return false;
}


function readFilelist(directoryItem) {
  $.ajax({
    type: 'POST',
    url: '/readFilelist',
    contentType: 'application/json',
    success: function (data) {
      $("#filelist").empty();
      var result = JSON.parse(data.ResultSet).result;
      if (result != "Failure") {
        $("#cwd").text(cwd);
        $("#filelist").append(
            "<li><a href='#uploadFileModal' id='upload' data-toggle='modal'>Upload file</a></li>"
        );
        $("#filelist").append(
            "<li class='divider' role='separator'></li>"
        );
        var fileList = JSON.parse(data.ResultSet).list;
        for (i = 0; i < fileList.length; i++) {
          $("#filelist").append(
              "<li class='dropdown-header'>" + fileList[i] + "</li>"
          );
        }
        // ダウンロードリストにリンクを詰め込む
        $("#download").empty();
        var username = JSON.parse(data.ResultSet).username;
        var tex = JSON.parse(data.ResultSet).tex;
        if (tex == "True") {
          $("#download").append(
              "<li><a href='../static/storage/" + username + "/" + cwd + "/document.tex' download='document.tex'>Download TeX file</a></li>"
          );
        }
        var pdf = JSON.parse(data.ResultSet).pdf;
        if (pdf == "True") {
          $("#download").append(
              "<li><a href='../static/storage/" + username + "/" + cwd + "/document.pdf' download='document.pdf'>Download PDF file</a></li>"
          );
        }
      }
    }
  });
  return false;
}


function upload() {
  var formData = new FormData($("#uploadForm")[0]);

  // processDataとcontentTypeのfalseは，formのファイルをPOSTする際には必要みたい
  $.ajax({
    url: '/upload',
    method: 'POST',
    processData: false,
    contentType: false,
    cache: false,
    data: formData,
    success: function (data) {
      var result = JSON.parse(data.ResultSet).result;
      if (result == "Success") {
        console.log("Success");
        readFilelist(cwd);
      } else {
        console.log("Failure");
      }
    }
  });
  return false;
}


function compile() {
  if (cwd != "") {
    // エディタのテキストを読み出し，JSONに
    // これをpythonに投げて，コンパイルリザルト，ログを受け取る
    // コンパイルに成功すれば，PDFファイルをindex.htmlに追加する
    editor.setReadOnly(true);
    var text = editor.getValue();
    var json = JSON.stringify({"text": text});

    $.ajax({
      type: 'POST',
      url: '/compile',
      data: json,
      contentType: 'application/json',
      success: function (data) {
        var result = JSON.parse(data.ResultSet).result;
        if (result == "Success") {
          var texlog = JSON.parse(data.ResultSet).texlog;

          // TeXログを挿入
          $("#result-detail").empty();
          for (i = 0; i < texlog.length; i++) {
            $("#result-detail").append(texlog[i] + "<br/>");
          }

          // PDFが存在していれば，RedPenログ，PDFファイルを挿入
          var existpdf = JSON.parse(data.ResultSet).existpdf;
          if (existpdf == "True") {
            // RedPenログを挿入
            var redpenout = JSON.parse(data.ResultSet).redpenout;
            var redpenerr = JSON.parse(data.ResultSet).redpenerr;
            $("#redpen-detail").empty();
            /*
             for (i = 0; i < redpenerr.length; i++) {
             $("#redpen-detail").append(redpenerr[i] + "<br/>");
             }
             */
            for (i = 0; i < redpenout.length; i++) {
              $("#redpen-detail").append(redpenout[i] + "<br/>");
            }

            var user = JSON.parse(data.ResultSet).user;
            var pdfpath = "../static/storage/" + user + "/" + cwd + "/document.pdf"
            // コンパイルするたびに最新のものを表示させたいので，pdfパスの後ろに?から始まるユニークな文字列を付ける
            // これをしないと，キャッシュのせいか，PDFファイルの表示が更新されない
            var timestamp = new Date().getTime();
            $("#preview").empty();
            $("#preview").append(
                "<object id='pdf' data='" + pdfpath + "?" + timestamp + "' type='application/pdf' width='595' height='600'></object>"
            );
          }
          readFilelist(cwd);
        }
      }
    });
    editor.setReadOnly(false);
    return false;
  }
}