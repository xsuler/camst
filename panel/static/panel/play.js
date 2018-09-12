function fromStr(str) {
    div = document.createElement('div');
    div.innerHTML = str.trim();
    return div.firstChild;
}

function alarm(){
    ws = new WebSocket('ws://127.0.0.1:3000/ws/alarm/');
    ws.onmessage = function(message) {
        data=JSON.parse(message.data);
        str='<table><tbody><tr><td>'+data['info']+'</td></tr></tbody></table>';
        list=document.getElementById("alarm");
        list.insertBefore(fromStr(str).children[0].children[0], list.childNodes[2]);
        console.log(data);
    };
}

alarm();
