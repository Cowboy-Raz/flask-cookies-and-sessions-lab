#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate

from models import db, Article, User, ArticleSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles')
def index_articles():
    articles = [ArticleSchema().dump(a) for a in Article.query.all()]
    return make_response(articles)

@app.route('/articles/<int:id>')
def show_article(id):
    # Step 1: Initialize the counter on the user's first request.
    # session.get() returns None (instead of raising a KeyError) when
    # 'page_views' doesn't exist yet, so "or 0" sets the starting value to 0.
    # If the key already exists, its current count is kept.
    session['page_views'] = session.get('page_views') or 0

    # Step 2: Count this request as one page view.
    # The count is stored in Flask's signed session cookie, so users can't
    # reset or change it from the browser's dev tools.
    session['page_views'] += 1

    # Step 3a: Paywall. After 3 views, block the article and return a 401.
    # The React client looks for this exact message to show its paywall screen.
    if session['page_views'] > 3:
        return {'message': 'Maximum pageview limit reached'}, 401

    # Step 3b: Under the limit, look up the requested article by its id.
    article = Article.query.filter_by(id=id).first()

    # If no article has that id, return a 404 instead of crashing.
    if article is None:
        return {'message': f'Article {id} not found'}, 404

    # Return the article as JSON (title, author, content, etc.) with a 200.
    return ArticleSchema().dump(article), 200


if __name__ == '__main__':
    app.run(port=5555)