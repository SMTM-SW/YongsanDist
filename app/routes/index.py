from flask import render_template

from app import app, COOKIE_KEY_ACCESS_TOKEN
from app.routes.oauth import get_oauth_url, request, redirect, url_for


@app.route("/", methods=['GET', 'POST'])
def index():
    if COOKIE_KEY_ACCESS_TOKEN in request.cookies:
        return redirect(url_for('project_list'))

    return render_template('pages/site/index.html',
                           signin=get_oauth_url())


@app.route("/about")
def about():
    return render_template('pages/site/about.html',
                           signin=get_oauth_url())
