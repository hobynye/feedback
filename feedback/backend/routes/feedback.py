from datetime import datetime

from flask_login import login_required
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from feedback.backend.models import Feedback, Volunteer, Role
from feedback.backend import db, twilio, app

feedback_bp = Blueprint('feedback_bp', __name__)


@feedback_bp.route('/api/feedback', methods={"GET"})
@login_required
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
    query = (db.session.query(Feedback, Volunteer, Role)
             .join(Volunteer, Feedback.submitted_by == Volunteer.id)
             .join(Role, Role.volunteer == Volunteer.id)
             .filter(Role.year == datetime.now().year)
             .order_by(Feedback.datetime.desc())
             ).limit(quantity).offset(offset).all()

    feedback = []
    for feedback_set in query:
        feedback.append({
            "author": feedback_set[1].name,
            "role": feedback_set[2].title,
            "color": feedback_set[2].color,
            "letter": feedback_set[2].letter,
            "severity": feedback_set[0].color,
            "body": feedback_set[0].body,
            "submitted": feedback_set[0].datetime.timestamp()
        })

    return jsonify(
        {
            "results": feedback,
            "quantity": len(feedback),
            "offset": offset
        }
    )


@feedback_bp.route('/api/feedback', methods={"POST"})
def create_feedback():
    parameters = request.get_json(force=True)
    req_params = ["author", "color", "body", "response"]
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
        response=bool(parameters["response"] in ["ASAP", "Yes"]),
        body=parameters["body"]
    )
    try:
        db.session.add(feedback)
        db.session.commit()
        if parameters["color"] == "Red" or parameters["response"] == "ASAP":
            name, phone = "Anonymous", ""
            volunteer = Volunteer.query.filter(Volunteer.id == parameters["author"]).first()
            if volunteer:
                name = volunteer.name
                if volunteer.phone:
                    phone = " ({})".format(volunteer.phone)

            to_alert = Volunteer.query.filter(
                Volunteer.admin == True,
                Volunteer.alert == True
            ).all()

            for admin in to_alert:
                if admin.phone:
                    twilio.messages \
                        .create(
                        body="[{} Alert] From: {}{} - {}".format(
                            parameters["color"],
                            name,
                            phone,
                            parameters["body"]
                        ),
                        from_=app.config["TWILIO_NUMBER"],
                        to="+1{}".format(admin.phone)
                    )
        return jsonify({"success": True})
    except IntegrityError:
        return jsonify(
            {
                "success": False,
                "error": "User does not exist!"
            }
        ), 400
