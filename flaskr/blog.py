from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
) 
from werkzeug.exceptions import abort

from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, p.title, p.body, p.created, p.author_id, u.username'
        ' FROM posts p JOIN users u ON p.author_id = u.id'
        ' ORDER BY p.created DESC'
    ).fetchall()

    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('POST','GET'))
@login_required
def create():
    if request.method == 'POST':
        error = None
        title = request.form['title']
        body = request.form['body']

        if not title:
            error = 'Title is required'
        elif not body:
            error = 'Body is required'
        else:
            db = get_db()
            db.execute(
                    'INSERT INTO posts (title, body, author_id)'
                    ' VALUES (?, ?, ?)',
                    (title,body,g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
        flash(error)
    return render_template('blog/post_edit.html',post=None)

@bp.route('/<int:id>/update', methods=('GET','POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        error = None
        title = request.form['title']
        body = request.form['body']

        if not title:
            error = 'Title is required'
        elif not body:
            error = 'Body is required'
        else:
            db = get_db()
            db.execute(
                    'UPDATE posts SET '
                    ' title = ?, '
                    'body = ?'
                    ' WHERE id = ?',
                    (title,body,id),
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
        flash(error)
    return render_template('blog/post_edit.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM posts WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, p.title, p.body, p.created, p.author_id, u.username'
        ' FROM posts p JOIN users u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()
    
    if post is None:
        abort(404,"Post id {0} doesn't exist.".format(id))
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post