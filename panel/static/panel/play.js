function fromStr(str) {
    div = document.createElement('div');
    div.innerHTML = str.trim();
    return div.firstChild;
}

function alarm(){
    ws = new WebSocket('ws://127.0.0.1:3000/ws/alarm/');
    ws.onmessage = function(message) {
        data=JSON.parse(message.data);
        alarm=document.getElementById("alarm");
        alarm.textContent=data['info'];
    };
}

alarm();
