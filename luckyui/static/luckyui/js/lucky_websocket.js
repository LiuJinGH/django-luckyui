'use strict';
{
    const retry_delay = 5 * 1000 // 重试延时

    let on_open_callback_list = []
    let on_event_callback_list = []

    let socket_url = null
    let has_connect = false
    let has_error = null
    let socket = null
    let heartbeat_timer = null // 心跳
    let alive_timer = null // 活检
    let is_form_parent = false

    function init_websocket(is_force = false) {
        console.log('调用 init_websocket')
        console.log(socket)

        if (socket) {
            console.log('readyState:' + socket.readyState)
            console.log('OPEN:' + WebSocket.OPEN)
            console.log('test:' + socket.readyState === WebSocket.OPEN)
        }

        if (socket && socket.readyState === WebSocket.OPEN) {
            console.log('web_socket 初始化时发现已经有存活链接')
            if (is_force) {
                console.log('web_socket 初始化时强制关闭')
                socket.close(1000, "Web Client is closing the connection");
            }
            return;
        }

        console.log('初始化 websocket')

        if (window.location.protocol === 'http:'){
            socket_url = 'ws://' + window.location.host + '/ws/lucky-channels/'
        }else{
            socket_url = 'wss://' + window.location.host + '/ws/lucky-channels/'
        }

        socket = new WebSocket(socket_url,)
        console.log(socket)

        // 连接打开时的回调函数
        socket.onopen = function (event) {
            has_connect = true
            console.log("Websocket 已连接");
            console.log(on_event_callback_list)
            // 可以在这里发送初始化信息或者其他数据
        };

        // 连接接收数据
        socket.onmessage = function (event) {
            let msg_data = JSON.parse(event.data)
            console.log(msg_data)
            let has_called_list = []
            for (let callback_item of on_event_callback_list) {
                console.log(callback_item.type)
                if (callback_item.type === msg_data.type) {
                    // console.log('匹配到回调事件')
                    // 匹配成功，判断是否执行过
                    if (has_called_list.indexOf(callback_item.id) === -1) {
                        // 未执行过
                        has_called_list.push(callback_item.id)
                        callback_item.callback(msg_data.data)
                    }
                }
            }
        };

        // 连接关闭时的回调函数
        socket.onclose = function (event) {
            has_connect = false
            console.log("Websocket Connection closed.");
        };

        // 连接错误时的回调函数
        socket.onerror = function (error) {
            has_connect = false
            console.error("Error detected: " + error);
        };
    }

    function remove_event_callback(callback_id) {
        console.log('移除：' + callback_id + '出回调事件队列')
        for (let callback_item of on_event_callback_list) {
            if (callback_item.id === callback_id) {
                console.log('remove_event_callback success')
                on_event_callback_list.splice(on_event_callback_list.indexOf(callback_item), 1);
            }
        }
    }

    function add_event_callback(type, callback_id, callback) {
        console.log('添加：' + callback_id + '到回调事件队列')
        remove_event_callback(callback_id)
        let callback_item = {
            type: type,
            callback: callback,
            id: callback_id
        }
        on_event_callback_list.push(callback_item)
        return callback_item.id
    }

    const lucky_websocket = {
        socket,
        on_event_callback_list,
        init_websocket,
        add_event_callback,
        remove_event_callback
    }

    if (parent.window.lucky_websocket) {
        console.log('使用上层window的lucky_websocket')
        // 上层window已经实现了websocket，直接使用
        window.lucky_websocket = parent.window.lucky_websocket;
        is_form_parent = true
    } else {
        console.log('使用本window的lucky_websocket')
        // 还没有实现
        window.lucky_websocket = lucky_websocket;
    }

    window.addEventListener('load', ()=>{
        if (!is_form_parent) {
            console.log('onload: 初始化 websocket。is_form_parent：' + is_form_parent)
            window.lucky_websocket.init_websocket();
        } else {
            console.log('is_form_parent存在')
        }
    })

    window.addEventListener('beforeunload', ()=>{
        if (is_form_parent) {
            console.log('is_form_parent存在')
            if(window.lucky_websocket){
               console.log('释放window lucky_websocket引用')
                window.lucky_websocket = null
            }
        }
    })
}

