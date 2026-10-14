from flask import Flask, request, redirect, url_for, session, render_template_string, jsonify, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
import calendar


app = Flask(__name__)
app.secret_key = "ESCAPE"

import os

app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is missing")

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ["DB_NAME"],
    "ssl_ca": os.path.join(os.path.dirname(__file__), "ca.pem"),
    "ssl_verify_cert": True,
    "ssl_verify_identity": True,
    "connection_timeout": 15,
}

def db():
    return mysql.connector.connect(**DB_CONFIG)

def db():
    return mysql.connector.connect(
        **DB_CONFIG,
        use_pure=True
    )
    

def setup_database():
    print("1. Connecting to MySQL...")

    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            use_pure=True
        )

        print("2. MySQL connected!")

        cur = conn.cursor()

        print("3. Creating database...")
        cur.execute("CREATE DATABASE IF NOT EXISTS diary")
        conn = db()
        cur = conn.cursor()

        print("4. Database created/exists!")

        cur.close()
        conn.close()

        print("5. First connection closed!")

        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database="diary",
            use_pure=True
        )

        print("6. Connected to diary database!")

        cur = conn.cursor()

        print("7. Creating users table...")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)

        print("8. Users table done!")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS diary_entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                entry_date DATE NOT NULL,
                title VARCHAR(200),
                content TEXT,
                mood VARCHAR(30),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_date (user_id, entry_date),
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        print("9. Diary table done!")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                task VARCHAR(255) NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        print("10. Todo table done!")

        conn.commit()

        cur.close()
        conn.close()

        print("11. DATABASE SETUP COMPLETE!")

    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!")
        print("DATABASE ERROR:")
        print(e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!")
        raise
    
BASE_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root{
 --navy:#102a43;--blue:#1976d2;--sky:#eaf6ff;--soft:#f5faff;--line:#d7e8f5;
 --text:#203040;--muted:#70859a;--white:#fff;--green:#39a96b;--pink:#f08aa4;
 --shadow:0 18px 50px rgba(16,42,67,.10);--radius:22px;
}
*{box-sizing:border-box} body{margin:0;background:linear-gradient(135deg,#eef9ff,#f9fcff);
font-family:'DM Sans',sans-serif;color:var(--text)} button,input,textarea,select{font:inherit}
button{cursor:pointer}.app{min-height:100vh;display:flex}.sidebar{width:260px;background:linear-gradient(180deg,#0d2942,#174d73);
color:white;padding:28px 18px;position:fixed;inset:0 auto 0 0;z-index:20}.brand{font-family:'Playfair Display',serif;font-size:28px;margin:0 10px 6px}
.tag{font-size:12px;color:#b9d9ef;margin:0 10px 28px}.nav a{display:block;color:#dcefff;text-decoration:none;padding:13px 14px;border-radius:14px;margin:5px 0}
.nav a:hover,.nav a.active{background:rgba(255,255,255,.13)}.userbox{position:absolute;left:18px;right:18px;bottom:22px;background:rgba(255,255,255,.10);padding:14px;border-radius:16px;font-size:13px}
.userbox strong{display:block}.main{margin-left:260px;width:calc(100% - 260px);padding:30px}.topbar{display:flex;justify-content:space-between;align-items:center;gap:15px;margin-bottom:25px}
.page-title{font-family:'Playfair Display',serif;font-size:34px;margin:0}.sub{color:var(--muted);margin-top:4px}.grid{display:grid;grid-template-columns:1.15fr .85fr;gap:22px}.card{background:rgba(255,255,255,.92);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:22px}
.card h3{margin:0 0 15px;font-family:'Playfair Display',serif;font-size:23px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:22px}.stat{padding:18px;border-radius:18px;background:linear-gradient(135deg,#eef8ff,#fff);border:1px solid var(--line)}
.stat .num{font-size:28px;font-weight:700;color:var(--navy)}.stat small{color:var(--muted)}.btn{border:0;border-radius:13px;padding:11px 16px;background:var(--blue);color:white;font-weight:700;box-shadow:0 7px 18px rgba(25,118,210,.22)}
.btn.secondary{background:#e8f4ff;color:#1765a8;box-shadow:none}.btn.danger{background:#ffecef;color:#b63855;box-shadow:none}.row{display:flex;gap:10px;align-items:center}.input,.textarea,.select{width:100%;border:1px solid var(--line);background:#fbfeff;border-radius:13px;padding:12px 14px;outline:none}.input:focus,.textarea:focus,.select:focus{border-color:#75b9e8;box-shadow:0 0 0 4px #eaf6ff}.textarea{min-height:330px;resize:vertical;line-height:1.8}.diary-title{font-family:'Playfair Display',serif;font-size:28px;border:0;background:transparent;padding:5px 0}.diary-title:focus{outline:none}.mood-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.mood{border:1px solid var(--line);background:#fff;border-radius:15px;padding:13px 8px;text-align:center}.mood input{display:none}.mood label{display:block;cursor:pointer}.mood:has(input:checked){border-color:#4ca6df;background:#eef9ff}.calendar{display:grid;grid-template-columns:repeat(7,1fr);gap:7px}.cal-head{font-size:11px;color:var(--muted);text-align:center}.day{padding:9px 2px;text-align:center;border-radius:10px;text-decoration:none;color:var(--text);border:1px solid transparent}.day:hover{background:#eaf6ff}.day.today{background:#dff1ff;border-color:#7bc0ec;font-weight:700}.day.has-entry{background:#e8f8ef;color:#197048}.day.empty{visibility:hidden}.entry-list{max-height:420px;overflow:auto}.entry{display:flex;justify-content:space-between;gap:10px;padding:13px 0;border-bottom:1px solid var(--line)}.entry:last-child{border-bottom:0}.entry a{color:var(--navy);text-decoration:none;font-weight:700}.muted{color:var(--muted);font-size:13px}.todo{display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--line)}.todo.done span{text-decoration:line-through;color:#9aa9b5}.flash{padding:12px 15px;border-radius:13px;background:#e9f8ef;color:#216b46;margin-bottom:15px}.auth{min-height:100vh;display:grid;place-items:center;padding:25px;background:radial-gradient(circle at 10% 10%,#cdeeff,transparent 35%),linear-gradient(135deg,#edf9ff,#f8fcff)}
.authbox{width:min(980px,100%);display:grid;grid-template-columns:1fr 1fr;background:white;border-radius:30px;overflow:hidden;box-shadow:0 25px 80px rgba(16,42,67,.16)}.authhero{padding:55px;background:linear-gradient(145deg,#0e3655,#217db3);color:white;position:relative}.authhero h1{font:700 55px 'Playfair Display',serif;margin:0 0 12px}.authhero p{color:#d9efff;line-height:1.7}.bubble{position:absolute;width:150px;height:150px;border-radius:50%;background:rgba(255,255,255,.07);right:-40px;bottom:30px}.authform{padding:50px}.authform h2{font:600 32px 'Playfair Display',serif;margin:0 0 8px}.field{margin:15px 0}.field label{display:block;font-size:13px;font-weight:700;margin-bottom:7px}.full{width:100%}.link{color:#1872b7;text-decoration:none;font-weight:700}.hamb{display:none}
@media(max-width:900px){.sidebar{transform:translateX(-100%);transition:.25s}.sidebar.open{transform:translateX(0)}.main{margin-left:0;width:100%;padding:20px}.hamb{display:block;border:0;background:#e7f5ff;border-radius:12px;padding:10px}.grid{grid-template-columns:1fr}.stats{grid-template-columns:1fr 1fr}.authbox{grid-template-columns:1fr}.authhero{display:none}}
@media(max-width:560px){.stats{grid-template-columns:1fr}.mood-grid{grid-template-columns:repeat(2,1fr)}.page-title{font-size:28px}.card{padding:17px}.topbar{align-items:flex-start}.calendar{gap:3px}.day{padding:8px 0;font-size:13px}}
"""

LAYOUT = r"""
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title or 'Escape Diary' }}</title><style>{{ style|safe }}</style>
</head><body><div class="app">
<aside class="sidebar" id="side"><div class="brand">Escape ✦</div><p class="tag">a little place for your thoughts</p>
<nav class="nav">
<a href="{{url_for('dashboard')}}" class="{{'active' if request.endpoint=='dashboard' else ''}}">⌂ Dashboard</a>
<a href="{{url_for('calendar_page')}}" class="{{'active' if request.endpoint=='calendar_page' else ''}}">▣ My Calendar</a>
<a href="{{url_for('mood_page')}}" class="{{'active' if request.endpoint=='mood_page' else ''}}">♡ Weekly Mood</a>
<a href="{{url_for('todo_page')}}" class="{{'active' if request.endpoint=='todo_page' else ''}}">✓ To-do List</a>
<a href="{{url_for('logout')}}">↪ Logout</a></nav>
<div class="userbox"><strong>{{session.get('name','Writer')}}</strong><span>Keep writing your story ✨</span></div></aside>
<main class="main"><div class="topbar"><div class="row"><button class="hamb" onclick="document.getElementById('side').classList.toggle('open')">☰</button>
<div><h1 class="page-title">{{heading}}</h1><div class="sub">{{subheading}}</div></div></div>
{% if session.get('user_id') %}<div class="muted">{{today}}</div>{% endif %}</div>
{% with messages=get_flashed_messages() %}{% for msg in messages %}<div class="flash">{{msg}}</div>{% endfor %}{% endwith %}
{{body|safe}}</main></div></body></html>
"""

def page(body, heading, subheading):
    return render_template_string(LAYOUT, style=BASE_STYLE, body=body, heading=heading,
                                  subheading=subheading, today=date.today().strftime("%A, %d %B %Y"), title=heading)

AUTH_STYLE = BASE_STYLE

@app.route("/", methods=["GET"])
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template_string(r"""<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Escape Diary</title><style>""" + AUTH_STYLE + r"""</style></head><body><div class="auth"><div class="authbox">
<div class="authhero"><h1>Escape ✦</h1><p>Your private little corner of the internet—write freely, track your moods, plan your days, and look back at the moments that made you.</p><div class="bubble"></div></div>
<div class="authform"><h2>Welcome back</h2><p class="sub">Sign in to continue your diary.</p>
<form method="post" action="/login"><div class="field"><label>USERNAME</label><input class="input" name="username" required></div>
<div class="field"><label>PASSWORD</label><input class="input" type="password" name="password" required></div>
<button class="btn full">Open my diary ✦</button></form>
<p class="sub" style="margin-top:20px">New here? <a class="link" href="/signup">Create an account</a></p></div></div></div></body></html>""")

@app.post("/login")
def login():
    username, password = request.form["username"].strip(), request.form["password"]
    conn=db(); cur=conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username=%s",(username,)); u=cur.fetchone()
    cur.close(); conn.close()
    if u and check_password_hash(u["password"], password):
        session["user_id"]=u["id"]; session["name"]=u["firstname"]
        return redirect(url_for("dashboard"))
    flash("Username or password is incorrect.")
    return redirect(url_for("home"))

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        f=request.form["firstname"].strip(); l=request.form["lastname"].strip()
        u=request.form["username"].strip(); p=request.form["password"]
        if not all([f,l,u,p]): flash("Please fill in every field."); return redirect(url_for("signup"))
        try:
            conn=db(); cur=conn.cursor()
            cur.execute("INSERT INTO users(firstname,lastname,username,password) VALUES(%s,%s,%s,%s)",
                        (f,l,u,generate_password_hash(p)))
            conn.commit(); cur.close(); conn.close()
            flash("Account created. Welcome to Escape!")
            return redirect(url_for("home"))
        except Error as e:
            flash("That username is already in use.")
            return redirect(url_for("signup"))
    return render_template_string(r"""<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Create account</title><style>""" + AUTH_STYLE + r"""</style></head><body><div class="auth"><div class="authbox">
<div class="authhero"><h1>Begin ✦</h1><p>There is no perfect way to journal. Just make this space yours.</p></div>
<div class="authform"><h2>Create your diary</h2><p class="sub">Your memories deserve a beautiful home.</p>
<form method="post"><div class="field"><label>FIRST NAME</label><input class="input" name="firstname" required></div>
<div class="field"><label>LAST NAME</label><input class="input" name="lastname" required></div>
<div class="field"><label>USERNAME</label><input class="input" name="username" required></div>
<div class="field"><label>PASSWORD</label><input class="input" type="password" name="password" minlength="6" required></div>
<button class="btn full">Create my diary ✦</button></form>
<p class="sub" style="margin-top:20px">Already have an account? <a class="link" href="/">Sign in</a></p></div></div></div></body></html>""")

def require_login():
    if not session.get("user_id"): return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    r=require_login()
    if r:return r
    uid=session["user_id"]; conn=db(); cur=conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) c FROM diary_entries WHERE user_id=%s",(uid,)); entries=cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) c FROM todos WHERE user_id=%s AND completed=0",(uid,)); pending=cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) c FROM diary_entries WHERE user_id=%s AND entry_date=%s",(uid,date.today())); written=cur.fetchone()["c"]
    cur.execute("SELECT * FROM diary_entries WHERE user_id=%s ORDER BY entry_date DESC LIMIT 7",(uid,)); recent=cur.fetchall()
    cur.execute("SELECT * FROM todos WHERE user_id=%s ORDER BY completed,created_at DESC LIMIT 5",(uid,)); todos=cur.fetchall()
    cur.close(); conn.close()
    body=render_template_string(r"""
<div class="stats"><div class="stat"><div class="num">{{entries}}</div><small>Diary entries</small></div>
<div class="stat"><div class="num">{{pending}}</div><small>Tasks waiting</small></div>
<div class="stat"><div class="num">{{'✓' if written else '—'}}</div><small>Today's page</small></div></div>
<div class="grid"><section class="card"><h3>Recently written ✍️</h3><div class="entry-list">
{% for e in recent %}<div class="entry"><div><a href="{{url_for('editor', d=e.entry_date)}}">{{e.title or 'Untitled page'}}</a><div class="muted">{{e.entry_date}} · {{e.mood or 'No mood'}}</div></div><span>{{'♥' if e.mood else '·'}}</span></div>{% else %}<p class="muted">Your first page is waiting for you.</p>{% endfor %}</div>
<a class="btn secondary" href="{{url_for('editor',d=date.today())}}">Write today ✦</a></section>
<section class="card"><h3>Little things to do ✓</h3><form method="post" action="/todo/add" class="row"><input class="input" name="task" placeholder="Add a tiny task..." required><button class="btn">+</button></form>
{% for t in todos %}<div class="todo {{'done' if t.completed else ''}}"><form method="post" action="/todo/toggle/{{t.id}}"><button class="btn secondary">{{'✓' if t.completed else '○'}}</button></form><span>{{t.task}}</span></div>{% else %}<p class="muted">Nothing here yet. Enjoy the quiet. 🌙</p>{% endfor %}
<a class="link" href="{{url_for('todo_page')}}">View all tasks →</a></section></div>""", entries=entries,pending=pending,written=written,recent=recent,todos=todos,date=date.today())
    return page(body,"Good day, "+session["name"]+" ✨","What would you like to remember today?")

@app.route("/calendar")
def calendar_page():
    r=require_login()
    if r:return r
    y=int(request.args.get("year",date.today().year)); m=int(request.args.get("month",date.today().month))
    cal=calendar.Calendar(firstweekday=0)
    conn=db(); cur=conn.cursor(dictionary=True); cur.execute("SELECT entry_date FROM diary_entries WHERE user_id=%s",(session["user_id"],))
    dates={x["entry_date"] for x in cur.fetchall()}; cur.close(); conn.close()
    cells=[]
    for d in cal.monthdatescalendar(y,m):
        for x in d:
            cells.append(x)
    body=render_template_string(r"""
<section class="card"><div class="row" style="justify-content:space-between;margin-bottom:18px">
<a class="btn secondary" href="?year={{prev.year}}&month={{prev.month}}">←</a><h3>{{monthname}} {{year}}</h3><a class="btn secondary" href="?year={{nxt.year}}&month={{nxt.month}}">→</a></div>
<div class="calendar">{% for h in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'] %}<div class="cal-head">{{h}}</div>{% endfor %}
{% for d in cells %}<a class="day {{'empty' if d.month!=month else ''}} {{'today' if d==today else ''}} {{'has-entry' if d in dates else ''}}" href="{{url_for('editor',d=d)}}">{{d.day}}</a>{% endfor %}</div>
<p class="muted" style="margin-top:18px">Green days already have a diary entry. Pick any date to write or edit its page.</p></section>""",
year=y,month=m,monthname=calendar.month_name[m],cells=cells,dates=dates,today=date.today(),
prev=(date(y,m,1)-timedelta(days=1)),nxt=(date(y,m,calendar.monthrange(y,m)[1])+timedelta(days=1)))
    return page(body,"Your calendar","Every date can hold a story.")

@app.route("/editor/<d>",methods=["GET","POST"])
def editor(d):
    r=require_login()
    if r:return r
    try: selected=datetime.strptime(d,"%Y-%m-%d").date()
    except: selected=date.today()
    uid=session["user_id"]; conn=db(); cur=conn.cursor(dictionary=True)
    if request.method=="POST":
        title=request.form.get("title","").strip() or "Untitled page"
        content=request.form.get("content",""); mood=request.form.get("mood","")
        cur.execute("""INSERT INTO diary_entries(user_id,entry_date,title,content,mood)
        VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE title=VALUES(title),content=VALUES(content),mood=VALUES(mood)""",
        (uid,selected,title,content,mood or None)); conn.commit()
        cur.close(); conn.close(); flash("Your page was saved safely ✦"); return redirect(url_for("editor",d=selected))
    cur.execute("SELECT * FROM diary_entries WHERE user_id=%s AND entry_date=%s",(uid,selected)); e=cur.fetchone()
    cur.close(); conn.close()
    body=render_template_string(r"""
<section class="card"><form method="post">
<div class="row" style="justify-content:space-between"><div><div class="muted">{{selected.strftime('%A, %d %B %Y')}}</div>
<input class="diary-title" name="title" value="{{e.title if e else ''}}" placeholder="Give this day a title..."></div>
<button class="btn">Save page ✦</button></div>
<textarea class="textarea" name="content" placeholder="Dear diary...&#10;&#10;Write whatever feels true today. There are no rules here.">{{e.content if e else ''}}</textarea>
<h3 style="margin-top:22px">How did today feel?</h3><div class="mood-grid">
{% for key,emoji,label in [('happy','☀️','Happy'),('okayish','🌤️','Okay-ish'),('neutral','🌙','Neutral'),('sad','🌧️','Sad')] %}
<div class="mood"><input id="{{key}}" type="radio" name="mood" value="{{key}}" {% if e and e.mood==key %}checked{% endif %}><label for="{{key}}"><div style="font-size:25px">{{emoji}}</div>{{label}}</label></div>{% endfor %}</div></form></section>""",e=e,selected=selected)
    return page(body,"Write your day","A calm canvas for the things you don't want to forget.")

@app.route("/mood")
def mood_page():
    r=require_login()
    if r:return r
    uid=session["user_id"]; today=date.today(); monday=today-timedelta(days=today.weekday()); sunday=monday+timedelta(days=6)
    conn=db(); cur=conn.cursor(dictionary=True)
    cur.execute("SELECT mood,COUNT(*) count FROM diary_entries WHERE user_id=%s AND entry_date BETWEEN %s AND %s AND mood IS NOT NULL GROUP BY mood",(uid,monday,sunday))
    counts={x["mood"]:x["count"] for x in cur.fetchall()}; cur.close(); conn.close()
    body=render_template_string(r"""
<section class="card"><h3>This week's mood</h3><p class="muted">{{start}} → {{end}}</p>
<canvas id="moodChart" height="120"></canvas>
<div class="stats" style="margin-top:20px"><div class="stat"><div class="num">{{total}}</div><small>Days tracked</small></div><div class="stat"><div class="num">{{happy}}</div><small>Happy days</small></div><div class="stat"><div class="num">{{sad}}</div><small>Sad days</small></div></div>
<p class="muted">Your chart is calculated weekly, not as separate daily reports. Add a mood while writing each day's page to build the week.</p></section>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script><script>
new Chart(document.getElementById('moodChart'),{type:'bar',data:{labels:['Happy','Okay-ish','Neutral','Sad'],datasets:[{label:'Days',data:[{{happy}},{{okay}},{{neutral}},{{sad}}],borderRadius:10}]},options:{plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,ticks:{precision:0}}}}});
</script>""",start=monday,end=sunday,total=sum(counts.values()),happy=counts.get("happy",0),okay=counts.get("okayish",0),neutral=counts.get("neutral",0),sad=counts.get("sad",0))
    return page(body,"Weekly mood","See the feeling of your week at a glance.")

@app.route("/todo")
def todo_page():
    r=require_login()
    if r:return r
    conn=db();cur=conn.cursor(dictionary=True);cur.execute("SELECT * FROM todos WHERE user_id=%s ORDER BY completed,created_at DESC",(session["user_id"],)); todos=cur.fetchall();cur.close();conn.close()
    body=render_template_string(r"""<section class="card"><h3>My little list ✓</h3><form method="post" action="/todo/add" class="row">
<input class="input" name="task" placeholder="What would make today easier?" required><button class="btn">Add task</button></form>
{% for t in todos %}<div class="todo {{'done' if t.completed else ''}}"><form method="post" action="/todo/toggle/{{t.id}}"><button class="btn secondary">{{'✓' if t.completed else '○'}}</button></form><span style="flex:1">{{t.task}}</span>
<form method="post" action="/todo/delete/{{t.id}}"><button class="btn danger">Delete</button></form></div>{% else %}<p class="muted">Your list is beautifully empty. 🌊</p>{% endfor %}</section>""",todos=todos)
    return page(body,"To-do list","Small steps count too.")

@app.post("/todo/add")
def todo_add():
    r=require_login()
    if r:return r
    task=request.form["task"].strip()
    if task:
        conn=db();cur=conn.cursor();cur.execute("INSERT INTO todos(user_id,task) VALUES(%s,%s)",(session["user_id"],task));conn.commit();cur.close();conn.close()
    return redirect(request.referrer or url_for("todo_page"))

@app.post("/todo/toggle/<int:tid>")
def todo_toggle(tid):
    r=require_login()
    if r:return r
    conn=db();cur=conn.cursor();cur.execute("UPDATE todos SET completed=1-completed WHERE id=%s AND user_id=%s",(tid,session["user_id"]));conn.commit();cur.close();conn.close()
    return redirect(request.referrer or url_for("todo_page"))

@app.post("/todo/delete/<int:tid>")
def todo_delete(tid):
    r=require_login()
    if r:return r
    conn=db();cur=conn.cursor();cur.execute("DELETE FROM todos WHERE id=%s AND user_id=%s",(tid,session["user_id"]));conn.commit();cur.close();conn.close()
    return redirect(request.referrer or url_for("todo_page"))

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("home"))


try:
    setup_database()
except Error:
    app.logger.exception("Database initialization failed")
    raise

if __name__ == "__main__":
    app.run(debug=False)

