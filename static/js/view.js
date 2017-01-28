var group = "";
var groups = [];
var datelist = [];
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
    groups = respjson.groups;
    for (var i = 0, len = groups.length; i < len; i++) {
      groupdiv.append(createGroup(groups[i]));
    }
  }).catch((err) => {
    console.error(err)
  })
}

function groupClick(groupname) {
  console.log("select: " + groupname);
  group = groupname;
  renderDatepicker();
  renderMessageList();
}

function renderDatepicker() {
  var fetchstr = "/fetch?type=date&groups=" + group
  fetch(fetchstr)
  .then((resp) => resp.json())
  .then((respjson) => {
    datelist = respjson.dates;
    $("#datepicker").datepicker('setStartDate', new Date(datelist[0]))
    $("#datepicker").datepicker('setEndDate', new Date(datelist[datelist.length-1]))
  }).catch((err) => {
    console.error(err)
  })
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

function initDatepicker() {
  $("#datepicker").datepicker({
    format: 'YYYY/DD/MM',
    clearBtn: true,
    beforeShowDay: function(date) {
      datestr = moment(date).format('YYYY-MM-DD');
      return datelist.some(x => x ==datestr);
    },
  });
  $("#datepicker").on('changeDate', handleDatePicker);
}

window.onload = function() {
  renderGroupList();
  initDatepicker();
}
