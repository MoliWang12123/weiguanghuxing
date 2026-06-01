from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from flask import Flask, g, jsonify, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "glowcare.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "glow-care-course-design"


def get_db() -> sqlite3.Connection:
    """Return a request-scoped SQLite connection."""
    if "db" not in g:
        DATA_DIR.mkdir(exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_: object | None = None) -> None:
    """Close the request-scoped database connection."""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def query_all(sql: str, params: Iterable[object] = ()) -> list[sqlite3.Row]:
    return get_db().execute(sql, tuple(params)).fetchall()


def execute(sql: str, params: Iterable[object] = ()) -> None:
    conn = get_db()
    conn.execute(sql, tuple(params))
    conn.commit()


def init_db() -> None:
    """Create tables and seed initial content when the database is empty."""
    DATA_DIR.mkdir(exist_ok=True)
    with app.app_context():
        conn = get_db()
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                author TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                tips TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL,
                emotion TEXT NOT NULL,
                content TEXT NOT NULL,
                reply TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        story_count = conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
        article_count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        if story_count == 0:
            conn.executemany(
                "INSERT INTO stories(title,category,author,summary,content,created_at) VALUES(?,?,?,?,?,?)",
                [
                    (
                        "夜班走廊里的小纸条",
                        "护士暖心瞬间",
                        "微光编辑部",
                        "一张写着谢谢的纸条，让漫长夜班多了一束微光。",
                        "凌晨两点，护士站的灯仍然亮着。术后患者因为疼痛难以入睡，值班护士反复巡视、评估疼痛等级并协助调整体位。第二天清晨，床头柜上留下了一张小纸条：谢谢你昨晚一直在。护理的价值有时并不宏大，却藏在一次俯身、一次倾听和一次及时回应里。",
                        "2026-05-12",
                    ),
                    (
                        "康复训练的第七步",
                        "患者康复故事",
                        "微光编辑部",
                        "从不敢下床到独立走完走廊，康复不是瞬间，而是被陪伴的过程。",
                        "一位术后患者最初害怕站立，担心伤口疼痛和身体失衡。护士与康复治疗师共同制定训练节奏，从床边坐起、扶栏站立到短距离步行，每一步都进行风险评估与鼓励反馈。第七次训练时，患者终于独立走到窗边。窗外的阳光并未改变病情本身，却让人重新确认了生活的方向。",
                        "2026-05-16",
                    ),
                    (
                        "把焦虑说出来",
                        "心理关怀",
                        "微光编辑部",
                        "护理沟通并非简单安慰，而是帮助患者重新获得安全感。",
                        "临床护理中的心理关怀强调倾听、共情与信息解释。面对焦虑患者，护士需要避免简单否定情绪，而应通过开放式提问了解担忧来源，再用清晰、温和的语言解释治疗流程。被理解本身就是一种干预，它能降低患者对未知情境的紧张感。",
                        "2026-05-20",
                    ),
                ],
            )
        if article_count == 0:
            conn.executemany(
                "INSERT INTO articles(title,category,summary,content,tips,created_at) VALUES(?,?,?,?,?,?)",
                [
                    (
                        "术后早期活动为什么重要",
                        "术后护理",
                        "在安全评估基础上进行早期活动，有助于促进循环和功能恢复。",
                        "术后活动需要遵循医嘱和个体化原则。护理人员通常会结合生命体征、疼痛程度、伤口情况和跌倒风险进行评估，再协助患者逐步完成床上活动、坐起、站立和步行训练。早期活动的意义在于减少长期卧床带来的不适，并帮助患者恢复日常生活信心。",
                        "不自行加量；头晕、胸闷、明显疼痛时应立即停止并告知医护人员。",
                        "2026-05-10",
                    ),
                    (
                        "儿童发热的温柔观察",
                        "儿童护理",
                        "关注精神状态、饮水量和伴随症状，比单一盯住体温数字更重要。",
                        "儿童发热时，家属常因体温变化而焦虑。护理宣教应强调综合观察：精神反应、进食饮水、尿量、皮疹、呼吸状态等均有参考价值。物理舒适护理要避免过度降温，保持环境通风、补充水分，并按医生建议使用退热药。",
                        "持续高热、精神差、呼吸急促、抽搐等情况应及时就医。",
                        "2026-05-18",
                    ),
                    (
                        "老年患者跌倒预防小课堂",
                        "老年护理",
                        "环境整理、鞋袜选择、夜间照明和起身节奏都属于护理安全管理。",
                        "老年患者跌倒风险与肌力下降、药物影响、视力变化和环境障碍有关。护理人员可通过床旁宣教、呼叫铃指导、地面防滑、夜灯设置和陪护提醒降低风险。跌倒预防不是限制活动，而是在安全边界内帮助老人维持活动能力。",
                        "起床遵循醒后先坐、坐稳再站、站稳再走的节奏。",
                        "2026-05-21",
                    ),
                    (
                        "护士情绪压力的自我照护",
                        "护士心理",
                        "护理工作者也需要被支持，稳定的照护者才能提供持续的照护。",
                        "面对高强度排班、患者病情变化和沟通压力，护士容易产生疲惫感。自我照护并不是逃避责任，而是职业可持续的一部分。可以通过短时呼吸放松、同伴支持、记录积极事件和规律作息来减少情绪消耗。",
                        "出现持续失眠、明显情绪低落或职业耗竭时，应主动寻求专业支持。",
                        "2026-05-22",
                    ),
                ],
            )
        msg_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        if msg_count == 0:
            conn.executemany(
                "INSERT INTO messages(nickname,emotion,content,reply,created_at) VALUES(?,?,?,?,?)",
                [
                    ("匿名护士A", "疲惫", "今天连续处理了很多琐碎沟通，感觉自己有点被消耗。", "你已经完成了很多看不见的照护。先喝口水，给自己两分钟安静呼吸。", "2026-05-23 21:10"),
                    ("实习同学", "紧张", "第一次跟临床操作，怕自己做得不够好。", "紧张说明你在认真对待。把流程拆小，先做到安全、规范、可复盘。", "2026-05-24 08:30"),
                ],
            )
        conn.commit()


@app.route("/")
def index():
    stories = query_all("SELECT * FROM stories ORDER BY id DESC LIMIT 3")
    articles = query_all("SELECT * FROM articles ORDER BY id DESC LIMIT 3")
    messages = query_all("SELECT * FROM messages ORDER BY id DESC LIMIT 2")
    return render_template("index.html", stories=stories, articles=articles, messages=messages)


@app.route("/stories")
def stories():
    category = request.args.get("category", "全部")
    if category == "全部":
        rows = query_all("SELECT * FROM stories ORDER BY id DESC")
    else:
        rows = query_all("SELECT * FROM stories WHERE category=? ORDER BY id DESC", [category])
    categories = ["全部", "护士暖心瞬间", "患者康复故事", "心理关怀"]
    return render_template("stories.html", stories=rows, categories=categories, current=category)


@app.route("/treehole", methods=["GET", "POST"])
def treehole():
    if request.method == "POST":
        nickname = request.form.get("nickname", "").strip() or "匿名来信"
        emotion = request.form.get("emotion", "平静").strip()
        content = request.form.get("content", "").strip()
        reply = make_reply(emotion, content)
        if content:
            execute(
                "INSERT INTO messages(nickname, emotion, content, reply, created_at) VALUES(?,?,?,?,?)",
                [nickname[:16], emotion[:12], content[:200], reply, datetime.now().strftime("%Y-%m-%d %H:%M")],
            )
        return redirect(url_for("treehole"))
    messages = query_all("SELECT * FROM messages ORDER BY id DESC")
    return render_template("treehole.html", messages=messages)


def make_reply(emotion: str, content: str) -> str:
    """Generate a gentle rule-based response for course demonstration."""
    if any(word in content for word in ["累", "疲惫", "压力", "崩溃"]):
        return "先把自己放回照护关系里。暂停三分钟、补水、做一次慢呼吸，都是有效的自我保护。"
    if emotion in ["焦虑", "紧张"]:
        return "把问题拆成最小步骤：先确认安全，再完成流程，最后复盘改进。你不需要一次做到完美。"
    if emotion in ["难过", "委屈"]:
        return "情绪被看见之后，人才更容易恢复力量。今天可以先允许自己慢一点。"
    return "愿这条微光回复陪你缓一缓。临床工作很重，但你并不是一个人在坚持。"


@app.route("/classroom")
def classroom():
    keyword = request.args.get("q", "").strip()
    category = request.args.get("category", "全部")
    sql = "SELECT * FROM articles WHERE 1=1"
    params: list[str] = []
    if category != "全部":
        sql += " AND category=?"
        params.append(category)
    if keyword:
        sql += " AND (title LIKE ? OR summary LIKE ? OR content LIKE ?)"
        like = f"%{keyword}%"
        params.extend([like, like, like])
    sql += " ORDER BY id DESC"
    articles = query_all(sql, params)
    categories = ["全部", "术后护理", "儿童护理", "老年护理", "护士心理"]
    return render_template("classroom.html", articles=articles, categories=categories, current=category, keyword=keyword)


@app.route("/gallery")
def gallery():
    albums = [
        {"title": "晨光里的护士站", "desc": "以柔和光影记录护理工作的安静秩序。", "img": "gallery_ward.svg"},
        {"title": "手写的感谢", "desc": "真实感谢常常简短，却足以抵达内心。", "img": "gallery_note.svg"},
        {"title": "窗边康复练习", "desc": "康复训练中最珍贵的是重新相信自己。", "img": "gallery_window.svg"},
        {"title": "花束与听诊器", "desc": "科学照护与人文关怀并不冲突。", "img": "gallery_flower.svg"},
    ]
    return render_template("gallery.html", albums=albums)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/api/messages")
def api_messages():
    rows = query_all("SELECT nickname, emotion, content, reply, created_at FROM messages ORDER BY id DESC LIMIT 20")
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
else:
    init_db()
