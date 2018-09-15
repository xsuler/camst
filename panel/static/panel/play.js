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
    ws = new WebSocket('ws://'+window.location.host+'/ws/alarm/');
    ws.onmessage = function(message) {
        data = JSON.parse(message.data);
        alarm = document.getElementById("alarm");
        alarm.textContent = data['info'];
    };
}

function view() {
    window.open('/panel/', '_self');
}
function camera() {
    window.open('/panel/camera/', '_self');
}
function config() {
    window.open('/panel/config/', '_self');
}
function userpage() {
    window.open('/panel/userpage/', '_self');
}

function getalarm() {
    window.open('/panel/getalarm/', '_self');
}

function refresh() {
    httpGet('/live/refresh/', (t) => {});
}


function delalarm(id) {
    url = '/panel/delalarm/';
    if (confirm("want to delete this record?")) {
        httpGet(url + id, (t) => {
            window.open('/panel/getalarm/', '_self');
        });
    }
}

function choosecam(id) {
    url = '/panel/camera/choosecam/';
    if (confirm("want to use this camera?")) {
        httpGet(url + id, (t) => {
            window.open('/panel/camera/', '_self');
        });
    }
}
function delregion(id) {
    url = '/panel/config/delregion/';
    if (confirm("want to delete this region?")) {
        httpGet(url + id, (t) => {
            window.open('/panel/config/', '_self');
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
