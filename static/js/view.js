var group = "";
var startstr = "";
var endstr = "";

function createGroup(data) {
  var div = $('<div>').addClass('group').text(data.nickname)
  div.click(function() { groupClick(data.name); })
  return div
}

function renderGroupList() {
  var fetchstr = "/fetch?type=groups";
  fetch(fetchstr)
  .then((resp) => resp.json())
  .then((respjson) => {
    var groupdiv = $('#groups');
    groupdiv.empty();
    var data = respjson.groups;
    for (var i = 0, len = data.length; i < len; i++) {
      groupdiv.append(createGroup(data[i]));
    }
  }).catch((err) => {
    console.error(err)
  })
}

function groupClick(groupname) {
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
    var fetchstr = "/fetch?type=friend&fname=" + name + "&fnickname=" + newName
    fetch(fetchstr).catch((err) => console.error(err));
  }
  renderGroupList();
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
