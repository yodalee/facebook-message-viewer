var group = "";
var startstr = "";
var endstr = "";

function renderGroupList() {
  var fetchstr = "/fetch?type=groups";
  fetch(fetchstr)
  .then((resp) => resp.json())
  .then((respjson) => {
    var groupdiv = document.getElementById("groups");
    var data = respjson.groups;
    for (var i = 0, len = data.length; i < len; i++) {
      var div = document.createElement('div');
      div.className = "group"
      div.innerHTML = data[i];
      div.onclick = function() { groupClick(this); }
      groupdiv.appendChild(div);
    }
  }).catch((err) => {
    console.error(err)
  })
}

function groupClick(obj) {
  groupname = obj.innerText
  console.log("select: " + groupname);
  group = groupname;
  renderMessageList();
}

function createMessage(data) {
  var time = $('<span>').addClass('time').html(data.time)
  var author = $('<span>').addClass('name').html(data.author)
  var meta = $('<div>').addClass('meta').append(time).append(author)
  var content = $('<p>').addClass('content').html(data.content)
  var message = $('<div>').addClass('message')
  message.append(meta).append(content)

  return message
}

function renderMessageList() {
  var fetchstr = "/fetch?type=message&group=" + group + "&startdate=" + startstr + "&enddate=" + endstr
  fetch(fetchstr)
  .then((resp) => resp.json())
  .then((respjson) => {
    var messagediv = $('#messages');
    messagediv.empty();
    var data = respjson.messages;
    for (var i = 0, len = data.length; i < len; i++) {
      messagediv.append(createMessage(data[i]));
    }
  }).catch((err) => {
    console.error(err)
  })
}

window.onload = function() {
  renderGroupList();
}
