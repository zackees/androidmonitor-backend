
// get the hosturl
const HOSTURL = window.location.protocol + "//" + window.location.host;
const ENDPOINT_LOGGED_IN = HOSTURL + "/v1/logged_in/operator";
const ENDPOINT_LIST_USERS = HOSTURL + "/v1/list/uids";

function is_logged_in(api_key, on_success, on_error) {
    fetch(ENDPOINT_LOGGED_IN, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'x-api-key': api_key
        }
    })
    .then(response => response.json())
    .then(data => on_success(data))
    .catch(error => on_error('Error:', error));
}

function list_users(api_key, on_success, on_error) {
    fetch(ENDPOINT_LIST_USERS, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'x-api-admin-key': api_key,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "start": "2023-03-18T02:47:14.133Z",
            "end": "2023-04-18T02:47:14.133Z"
        })
    })
    .then(response => response.json())
    .then(data => on_success(data))
    .catch(error => on_error('Error:', error));
}

function list_uploads(api_key, on_success, on_error) {
    fetch('https://androidmonitor.internetwatchdogs.org/v1/list/uploads', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'x-api-admin-key': api_key,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        "uid": "*",
        "start": "2023-03-18T02:51:29.612Z",
        "end": "2023-04-18T02:51:29.612Z",
        "appname": "*",
        "count": 100
    })
    })
    .then(response => response.json())
    .then(data => on_success(data))
    .catch(error => on_error(error));
}

is_logged_in(
    'test',
    function(data) { console.log(data); },
    function(err) { console.log(err); }
);

list_users(
    'test',
    function(data) { console.log(data); },
    function(err) { console.log(err); }
)

list_uploads(
    'test',
    function(data) { console.log(data); },
    function(err) { console.log(err); }
)