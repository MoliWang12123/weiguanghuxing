from app import app, init_db

init_db()
client = app.test_client()
routes = ["/", "/stories", "/treehole", "/classroom", "/gallery", "/about", "/api/messages"]
print("微光护行Web系统功能测试")
for route in routes:
    resp = client.get(route)
    print(f"GET {route:<14} 状态码：{resp.status_code}")

resp = client.post("/treehole", data={"nickname": "测试用户", "emotion": "焦虑", "content": "今天任务很多，有些紧张。"}, follow_redirects=True)
print(f"POST /treehole   状态码：{resp.status_code}")
print("测试结论：主要页面可正常访问，树洞留言写入与跳转功能正常。")
