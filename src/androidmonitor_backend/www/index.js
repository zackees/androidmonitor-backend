const HOSTURL = window.location.protocol + "//" + window.location.host;
const ENDPOINT_LOGGED_IN = HOSTURL + "/v1/logged_in/operator";
const ENDPOINT_LIST_USERS = HOSTURL + "/v1/list/uids";
const OPERATOR_KEY = "test"

async function is_logged_in(api_key) {
    try {
        const response = await fetch(ENDPOINT_LOGGED_IN, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'x-api-key': api_key
            }
        });
        const data = await response.json();
        return data;
    } catch (error) {
        throw new Error('Error:', error);
    }
}

async function list_users(api_key) {
    try {
        const response = await fetch(ENDPOINT_LIST_USERS, {
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
        });
        const data = await response.json();
        return data;
    } catch (error) {
        throw new Error('Error:', error);
    }
}

async function list_uploads(api_key) {
    try {
        const response = await fetch('https://androidmonitor.internetwatchdogs.org/v1/list/uploads', {
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
        });
        const data = await response.json();
        return data;
    } catch (error) {
        throw error;
    }
}

(async () => {
    try {
        const loggedInData = await is_logged_in(OPERATOR_KEY);
        console.log("Logged In:", loggedInData);
    } catch (err) {
        console.log(err);
    }

    try {
        const listUsersData = await list_users(OPERATOR_KEY);
        console.log("List users:", listUsersData);
    } catch (err) {
        console.log(err);
    }

    try {
        const listUploadsData = await list_uploads(OPERATOR_KEY);
        console.log("List Uploads:", listUploadsData);
    } catch (err) {
        console.log(err);
    }
})();
