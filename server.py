from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import config
from dataclasses import dataclass

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
database = SQLAlchemy(app)


@dataclass()
class Users(database.Model):
    id: int
    login: int

    id = database.Column(database.Integer, primary_key=True)
    login = database.Column(database.Integer)


@dataclass()
class Categories(database.Model):
    id: int
    name: str

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(64))

@dataclass()
class Subs(database.Model):
    user_id: int
    category_id: int

    user_id = database.Column(database.Integer, primary_key=True)
    category_id = database.Column(database.Integer, primary_key=True)


config_categories_length = len(config.categories)
table_categories_length = len(database.session.execute(database.select(Categories)).all())

if config_categories_length > table_categories_length:
    for category in config.categories:
        database.session.add(Categories(name=category))
        database.session.commit()


@app.route("/start", methods=["POST", "GET"])
def register_user():
    if request.method == "POST":
        if Users.query.filter_by(login=request.json["login"]).first() is None:
            database.session.add(Users(login=request.json["login"]))
            database.session.commit()

    return {"OK": True}


@app.route("/sub/markup_info", methods=["POST", "GET"])
def sub_on_category():
    if request.method == "POST":
        categories = Categories.query.all()

        return jsonify(categories)


@app.route("/sub/to_sub", methods=["POST", "GET"])
def subscribe_user():
    result = {}
    if request.method == "POST":
        user_message = database.session.execute(database.select(Categories.id).filter_by(name=request.json["category"])).first()

        if user_message is not None :
            user_id = database.session.execute(database.select(Users.id).filter_by(login=request.json["login"])).first()

            check_if_sub = Subs.query.filter_by(user_id=user_id[0], category_id=user_message[0]).first()

            if check_if_sub is None:
                database.session.add(Subs(user_id=user_id[0], category_id=user_message[0]))
                database.session.commit()

                result = {"result_text": "круто! вы подписались на эту категорию"}

            else:
                result = {"result_text": "вы уже подписаны на эту категорию"}

    return result


@app.route("/unsub", methods=["POST", "GET"])
def unsub_on_category():
    user_id = database.session.execute(database.select(Users.id).filter_by(login=request.json["login"])).first()
    categories = database.session.execute(database.select(Subs.category_id).filter_by(user_id=user_id[0])).all()
    user_subs = []

    for category in categories:
        sub_categories = Categories.query.filter_by(id=category[0]).first()
        user_subs.append(sub_categories)

    return jsonify(user_subs)


@app.route("/unsub/to_unsub", methods=["POST", "GET"])
def unsubscribe_user():
    result = {}
    if request.method == "POST":
        user_id = database.session.execute(database.select(Users.id).filter_by(login=request.json["login"])).first()
        user_message = database.session.execute(database.select(Categories.id).filter_by(name=request.json["category"])).first()

        if user_message is not None:
            Subs.query.filter_by(user_id=user_id[0], category_id=user_message[0]).delete(synchronize_session=False)
            database.session.commit()

            result = {"result_text": "круто! вы отписались от этой категории"}

        else:
            result = {"result_text": "такой категории не существует"}

    return result


@app.route("/news", methods=["POST", "GET"])
def send_news():
    user_id = database.session.execute(database.select(Users.id).filter_by(login=request.json["login"])).first()
    categories = database.session.execute(database.select(Subs.category_id).filter_by(user_id=user_id[0])).all()
    user_subs = []

    for category in categories:
        sub_categories = Categories.query.filter_by(id=category[0]).first()
        user_subs.append(sub_categories)

    return jsonify(user_subs)


if __name__ == "__main__":
    app.run()
