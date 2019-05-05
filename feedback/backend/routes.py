from . import app, db
from .models import Feedback, Volunteer, Role
from flask import render_template, request, jsonify
from sqlalchemy.exc import IntegrityError
from datetime import datetime


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/api/feedback', methods={"GET"})
def list_feedback():
    quantity = int(request.args.get('qty', 10))
    offset = int(request.args.get('offset', 0))
    if 1 < quantity > 100:
        return jsonify(
            {
                "success": False,
                "error": "Invalid Quantity! (Valid Range [1,100])"
            }
        ), 400
    results = Feedback.query\
        .join(Volunteer,Feedback.submitted_by == Volunteer.id)\
        .with_entities(
            Volunteer.name,
            Feedback.id,
            Feedback.submitted_by,
            Feedback.datetime,
            Feedback.color,
            Feedback.body)\
        .limit(quantity).offset(offset).all()
    return jsonify(
        {
            "results": [
                {
                    "id": row.id,
                    "author": row.name,
                    "submitted": row.datetime.timestamp(),
                    "color": row.color,
                    "body": row.body
                } for row in results],
            "quantity": len(results),
            "offset": offset
        }
    )


@app.route('/api/feedback', methods={"POST"})
def create_feedback():
    parameters = request.get_json(force=True)
    req_params = ["author", "color", "body"]
    for param in req_params:
        if param not in parameters:
            return jsonify(
                {
                    "success": False,
                    "error": "No value '{}' value provided.".format(param)
                }
            ), 400
    feedback = Feedback(
        submitted_by=parameters["author"],
        color=parameters["color"],
        body=parameters["body"]
    )
    try:
        db.session.add(feedback)
        db.session.commit()
        return jsonify({"success": True})
    except IntegrityError:
        return jsonify(
            {
                "success": False,
                "error": "User does not exist!"
            }
        ), 400


@app.route('/api/users', methods={"GET"})
def list_volunteers():
    volunteers = Role.query \
        .filter(Role.year == datetime.now().year)\
        .join(Volunteer, Role.volunteer == Volunteer.id)\
        .with_entities(
            Volunteer.id,
            Volunteer.name)
    return jsonify(
        {
            "volunteers": [{
                "id": row.id,
                "name": row.name
            } for row in volunteers]
        }
    )