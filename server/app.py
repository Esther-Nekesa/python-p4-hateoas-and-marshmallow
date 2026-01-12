#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///newsletters.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

ma = Marshmallow(app)
api = Api(app)

# -----------------------
# SCHEMA (HATEOAS)
# -----------------------
class NewsletterSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Newsletter
        load_instance = True

    id = ma.auto_field()
    title = ma.auto_field()
    published_at = ma.auto_field()

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "newsletterbyid",
                values={"id": "<id>"}
            ),
            "collection": ma.URLFor("newsletters"),
        }
    )


newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many=True)

# -----------------------
# ROUTES
# -----------------------
class Index(Resource):
    def get(self):
        return make_response(
            {"message": "Welcome to the Newsletter RESTful API"},
            200
        )

api.add_resource(Index, "/", endpoint="index")


class Newsletters(Resource):
    def get(self):
        newsletters = Newsletter.query.all()
        return make_response(
            newsletters_schema.dump(newsletters),
            200
        )

    def post(self):
        newsletter = Newsletter(
            title=request.form["title"],
            body=request.form["body"],
        )

        db.session.add(newsletter)
        db.session.commit()

        return make_response(
            newsletter_schema.dump(newsletter),
            201
        )

api.add_resource(Newsletters, "/newsletters", endpoint="newsletters")


class NewsletterByID(Resource):
    def get(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        return make_response(
            newsletter_schema.dump(newsletter),
            200
        )

    def patch(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()

        for attr in request.form:
            setattr(newsletter, attr, request.form[attr])

        db.session.commit()

        return make_response(
            newsletter_schema.dump(newsletter),
            200
        )

    def delete(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        db.session.delete(newsletter)
        db.session.commit()

        return make_response("", 204)

api.add_resource(
    NewsletterByID,
    "/newsletters/<int:id>",
    endpoint="newsletterbyid"
)

# -----------------------
# RUN SERVER
# -----------------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)
