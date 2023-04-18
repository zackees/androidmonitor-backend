const HOSTURL = window.location.protocol + '//' + window.location.host;
const xApiKey = 'test';

/**
 *
 */
const endpoints = {
  loggedInOperator: 'v1/logged_in/operator',
  listUids: 'v1/list/uids',
  listUploads: 'v1/list/uploads',
};

async function post(endpoint, params = {}) {
  return call(endpoint, params, 'POST');
}

/**
 *
 */
async function call(endpoint, params = {}, method = 'GET') {
  let paramString = '';
  const parts = [];

  if (method === 'GET') {
    for (const key of Object.keys(params)) {
      parts.push(`${key}=${encodeURIComponent(params[key])}`);
    }

    if (parts.length > 0) {
      paramString = '?' + parts.join('&');
    }
  }

  const url = `${HOSTURL}/${endpoint}${paramString}`;

  const command = {
    method,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      'x-api-key': xApiKey,
      'x-api-admin-key': xApiKey,
    },
  };

  if (method === 'POST') {
    command.body = JSON.stringify(params);
  }

  const response = await fetch(url, command);

  return response.json();
}

$(document).ready(async function () {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);

  const app = $('#app');
  const accordion = $('#accordion');
  const password = $('#password');
  const listUsers = $('#listUsers');
  const listUploads = $('#listUploads');

  // Login Dialog
  const dialog = $('#login-dialog');
  dialog.dialog({
    autoOpen: true,
    modal: true,
  });
  dialog.parent().find('.ui-dialog-titlebar-close').hide();
  dialog.find('form').on('submit', async function (event) {
    //
    event.preventDefault();
    const loggedIn = await login(password.val());

    if (loggedIn) {
      dialog.dialog('close');
      app.show();
    }
  });

  // Video Dialog
  const videoDialog = $('#video-dialog');
  videoDialog.dialog({
    autoOpen: false,
    modal: true,
  });

  // App
  accordion.accordion({
    collapsible: true,
    heightStyle: 'content',
  });

  // List Users
  const userStartDate = $('#userStartDate');
  const userEndDate = $('#userEndDate');
  const userStartTime = $('#userStartTime');
  const userEndTime = $('#userEndTime');
  const userResults = $('#userResults').hide();

  userStartDate.datepicker({
    showWeek: true,
    firstDay: 1,
    onSelect: () => {
      if (userStartTime.val() === '') {
        userStartTime.val('12:00 AM');
      }
    },
  });

  userEndDate.datepicker({
    showWeek: true,
    firstDay: 1,
    onSelect: () => {
      if (userEndTime.val() === '') {
        userEndTime.val('11:59 PM');
      }
    },
  });

  userStartTime.timepicker({
    timeFormat: 'h:mm TT',
    interval: 15,
    minTime: '00:00',
    maxTime: '11:59 PM',
    defaultTime: '12:00',
    startTime: '00:00',
    dynamic: false,
    dropdown: true,
    scrollbar: true,
    ampm: true,
  });

  userEndTime.timepicker({
    timeFormat: 'h:mm TT',
    interval: 15,
    minTime: '00:00',
    maxTime: '11:59 PM',
    defaultTime: '12:00',
    startTime: '00:00',
    dynamic: false,
    dropdown: true,
    scrollbar: true,
    ampm: true,
  });

  listUsers.click(async (e) => {
    listUsers.prop('disabled', true);
    listUsers.text('Searching...');
    const options = {
      start: getDatetime(userStartDate.val(), userStartTime.val(), yesterday),
      end: getDatetime(userEndDate.val(), userEndTime.val()),
    };
    const users = await post(endpoints.listUids, options);
    listUsers.prop('disabled', false);
    listUsers.text('Search');

    userResults.hide();
    let html = '';
    for (const user of users) {
      html += `<tr></tr>`;
    }

    userResults.find('tbody').html(html);
    userResults.show();
  });

  // Uploads
  const uploadsStartDate = $('#uploadsStartDate');
  const uploadsEndDate = $('#uploadsEndDate');
  const uploadsStartTime = $('#uploadsStartTime');
  const uploadsEndTime = $('#uploadsEndTime');
  const uploadsUid = $('#uploadsUid');
  const uploadsAppname = $('#uploadsAppname');
  const uploadsCount = $('#uploadsCount');
  const uploadResults = $('#uploadResults').hide();

  userStartTime.timepicker({
    timeFormat: 'h:mm TT',
    interval: 15,
    minTime: '00:00',
    maxTime: '11:59 PM',
    defaultTime: '12:00',
    startTime: '00:00',
    dynamic: false,
    dropdown: true,
    scrollbar: true,
    ampm: true,
  });

  userEndTime.timepicker({
    timeFormat: 'h:mm TT',
    interval: 15,
    minTime: '00:00',
    maxTime: '11:59 PM',
    defaultTime: '12:00',
    startTime: '00:00',
    dynamic: false,
    dropdown: true,
    scrollbar: true,
    ampm: true,
  });

  uploadsStartDate.datepicker({
    showWeek: true,
    firstDay: 1,
    onSelect: () => {
      if (userStartTime.val() === '') {
        userStartTime.val('12:00 AM');
      }
    },
  });

  uploadsEndDate.datepicker({
    showWeek: true,
    firstDay: 1,
    onSelect: () => {
      if (userEndTime.val() === '') {
        userEndTime.val('11:59 PM');
      }
    },
  });

  listUploads.click(async (e) => {
    listUploads.prop('disabled', true);
    listUploads.text('Searching...');

    const options = {
      start: getDatetime(
        uploadsStartDate.val(),
        uploadsStartTime.val(),
        yesterday
      ),
      end: getDatetime(uploadsEndDate.val(), uploadsEndTime.val()),
      count: uploadsCount.val(),
    };

    if (uploadsUid.val() !== '') {
      options.uid = uploadsUid.val();
    }

    if (uploadsAppname.val() !== '') {
      options.appname = uploadsAppname.val();
    }
    const uploads = await post(endpoints.listUploads, options);

    listUploads.prop('disabled', false);
    listUploads.text('Search');

    uploadResults.hide();
    let html = '';
    for (const upload of uploads) {
      html += `<tr>
        <td>${upload.id}</td>
        <td><button onclick="showVideo('${upload.uri_video}');">Watch</button></td>
        <td>${upload.appname}</td>
        <td>${upload.start}</td>
        <td>${upload.end}</td>
      </tr>`;
    }

    uploadResults.find('tbody').html(html);
    uploadResults.show();
  });
});

/**
 *
 */
function getDatetime(date, time, now = new Date()) {
  if (date === undefined || date === false || date === '') {
    date = `${now.getMonth()}/${now.getDate()}/${now.getFullYear()}`;
  }

  if (time === undefined || time === false || time === '') {
    time = `${now.getHours()}:${now.getMinutes()}`;
  }

  return new Date(`${date} ${time}`).toISOString();
}

/**
 *
 */
function showVideo(url) {
  const videoDialog = $('#video-dialog');
  videoDialog.html(`<video controls>
  <source src="${url}" type="video/mp4">
  Your browser does not support the video tag.
  </video>
  <br />
  <a href="${url}">Download</a>`);
  videoDialog.dialog('open');
}

/**
 *
 */
function setAppVisibility(app, showApp) {
  if (showApp === true) {
    app.show();
  } else {
    app.hide();
  }
}

/**
 *
 */
function isLoggedIn() {
  const password = localStorage.getItem('absolutelyNotAPassword');

  if (password === null) {
    return false;
  } else {
    return true;
  }
}

/**
 *
 */
async function login(password) {
  if (isLoggedIn()) {
    return true;
  }
  // @TODO am I passing up a password here or something?
  const result = await call(endpoints.loggedInOperator);
  if (result && result.ok === true) {
    localStorage.setItem('absolutelyNotAPassword', password);
    return true;
  } else {
    return false;
  }
}

/**
 *
 */
function addAccordianItem(title, data, accordian) {
  const newItemHTML = `<h3>${title}</h3><div>${data}</div>`;
  accordian.append(newItemHTML);
  accordian.accordion('refresh');
}
