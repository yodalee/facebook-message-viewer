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

function renderDatepicker() {
  $("#datepicker").datepicker({
    format: 'YYYY/DD/MM',
    clearBtn: true,
  });
  $("#datepicker").on('changeDate', handleDatePicker);
}

function handleDatePicker(ev) {
  $(this).datepicker('hide');
  // set text
  if (ev.date) {
    console.log("select: " + ev.date);
    startstr = moment(ev.date).format('YYYYMMDD');
    $('#Since').text(startstr);
  } else {
    startstr = "";
    $('#Since').text("Since");
  }
  renderMessageList();
}

function setFriendName(name, nickname) {
  var newName = prompt("Please enter the new name of "+ nickname, nickname);
  if (newName != null) {
    var fetchstr = "/fetch?type=friend&old=" + name + "&new=" + newName
    fetch(fetchstr).catch((err) => console.error(err));
  }
  renderMessageList();
}

function createMessage(data) {
  var time = $('<span>').addClass('time').html(data.time)
  var author = $('<span>').addClass('name').html(data.nickname)
  author.click(function() { setFriendName(data.name, data.nickname); })
  var meta = $('<div>').addClass('meta').append(time).append(author)
  var content = $('<p>').addClass('content').html(data.content)
  var message = $('<div>').addClass('message')
  message.append(meta).append(content)

  return message
}

function renderMessageList() {
  var fetchstr = "/fetch?type=message&group=" + group + "&startdate=" + startstr + "&enddate=" + endstr
  if (!group) {
    return;
  }
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
  renderDatepicker();
  renderGroupList();
}
