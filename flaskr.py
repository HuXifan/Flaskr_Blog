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
    '''这个视图显示数据库中存储的所有条目。它绑定在应用的根地址，并从数据库查询出文章的标题和正文。
    id 值最大的条目（最新的条目）会显示在最上方。
    从指针返回的行是按 select 语句中声明的列组织的元组。'''
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


# 添加条目
@app.route('/add', methods=['POST'])
def add_entry():
    '''这个视图允许已登入的用户添加新条目，并只响应 POST 请求，实际的表单显示在 show_entries 页。
    如果一切工作正常，我们会用 flash() 向下一次请求发送提示消息，并重定向回 show_entries 页:'''
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''登入通过与配置文件中的数据比较检查用户名和密码， 并设定会话中的 logged_in 键值。
    如果用户成功登入，那么这个键值会被设为 True ，并跳转回 show_entries 页。
      此外，会有消息闪现来提示用户登入成功。 如果发生一个错误，模板会通知，并提示重新登录。'''
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


# 登出
@app.route('/logout')
def logout():
    '''登出函数，做相反的事情，从会话中删除 logged_in 键。我们这里使用了一个简洁的方法：
    如果你使用字典的 pop()方法并传入第二个参数（默认），这个方法会从字典中删除这个键，如果这个键不存在则什么都不做。
    这很有用，因为我们不需要检查用户是否已经登入。'''
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    # init_db()
    app.run()
