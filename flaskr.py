# all the imports
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, \
    redirect, url_for, abort, render_template, flash

# create our little application
app = Flask(__name__)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


# 初始化数据库
def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        # 应用对象的 open_resource() 方法是一个很方便的辅助函数，可以打开应用提供的资源。
        # 这个函数从资源所在位置（你的flaskr文件夹）打开文件，并允许读取它。在此用它来在数据库连接上执行脚本。
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# 显示条目
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


# 添加条目
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    # init_db()
    app.run()
