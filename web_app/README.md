# 微光护行：护理人文与生命治愈网站

## 项目简介
本项目为《Python程序设计》期末考核作品，选题为Web开发方向。系统采用Python Flask框架实现，围绕护理人文、生命教育、心理关怀和温柔健康科普构建一个可访问、可交互、可扩展的网站作品。

## 功能模块
- 首页：展示项目主题、核心板块、最新内容。
- 微光故事：呈现护士暖心瞬间与患者康复故事。
- 护士树洞：支持匿名情绪留言、压力疏导和数据写入。
- 生命小课堂：健康科普文章检索和分类阅读。
- 光影相册：护理人文摄影和手绘插画展示。
- 关于项目：说明设计理念、技术架构和部署方式。

## 本地运行
```bash
cd web_app
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
浏览器访问：http://127.0.0.1:5000

## 测试
```bash
python run_tests.py
```

## 部署建议
可部署至Render、PythonAnywhere、Railway或学校服务器。启动命令为：
```bash
gunicorn app:app
```
如使用Render，需要将根目录设置为`web_app`，并配置`requirements.txt`。
