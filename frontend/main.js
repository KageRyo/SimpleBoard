// 範例：登入、取得留言、發送留言
const apiBase = "http://localhost:8000";

async function login(username, password) {
    const resp = await fetch(`${apiBase}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });
    if (!resp.ok) throw new Error("登入失敗");
    return await resp.json();
}

async function getMessages(token) {
    const resp = await fetch(`${apiBase}/messages`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    if (!resp.ok) throw new Error("取得留言失敗");
    return await resp.json();
}

async function postMessage(token, message) {
    const resp = await fetch(`${apiBase}/message`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ message })
    });
    if (!resp.ok) throw new Error("留言失敗");
    return await resp.json();
}

// 你可以在這裡串接 UI 事件
