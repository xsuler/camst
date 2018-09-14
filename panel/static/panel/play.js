function httpGet(url, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    };
    xmlHttp.open("GET", url, true);
    xmlHttp.send(null);
}

function fromStr(str) {
    div = document.createElement('div');
    div.innerHTML = str.trim();
    return div.firstChild;
}

function socket() {
    ws = new WebSocket('ws://127.0.0.1:3000/ws/alarm/');
    ws.onmessage = function(message) {
        data = JSON.parse(message.data);
        alarm = document.getElementById("alarm");
        alarm.textContent = data['info'];
    };
}

function userpage() {
    window.open('/panel/userpage/', '_self');
}

function getalarm() {
    window.open('/panel/getalarm/', '_self');
}

function refresh() {
    httpGet('/live/refresh/', (t) => {
    });
}
function delalarm(id) {
    url = '/panel/delalarm/';
    if (confirm("want to delete this record?")) {
        httpGet(url + id, (t) => {
            window.open('/panel/getalarm/', '_self');
        });
    }
}

function deluser(id) {
    url = '/panel/userpage/deluser/';
    if (confirm("want to delete this user?")) {
        httpGet(url + id, (t) => {
            window.open('/panel/userpage/', '_self');
        });
    }
}
socket();
