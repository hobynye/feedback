from datetime import datetime, date
import csv
import io

from flask_login import login_required
from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from feedback.backend.models import Feedback, Volunteer, Role
from feedback.backend import db, twilio, app

feedback_bp = Blueprint('feedback_bp', __name__)


@feedback_bp.route('/api/feedback', methods={"GET"})
@login_required
def list_feedback():
    year = int(request.args.get('year', datetime.now().year))
    download = bool(request.args.get('download', False))

    if year < 2019:
        return jsonify(
            {
                "success": False,
                "error": "Invalid Year!"
            }
        ), 400
    query = (db.session.query(Feedback, Volunteer, Role)
             .join(Volunteer, Feedback.submitted_by == Volunteer.id)
             .join(Role, Role.volunteer == Volunteer.id)
             .filter(
                or_(Role.year == 1970, Role.year == datetime.now().year),
                Feedback.datetime.between(
                    date(year, 1, 1),
                    date(year, 12, 31)
                )
                )
             .order_by(Feedback.datetime.desc())
             ).all()

    feedback = []
    for feedback_set in query:
        feedback.append({
            "id": feedback_set[0].id,
            "author": feedback_set[1].name,
            "role": feedback_set[2].title,
            "color": feedback_set[2].color,
            "letter": feedback_set[2].letter,
            "severity": feedback_set[0].color,
            "body": feedback_set[0].body,
            "handled": feedback_set[0].handled,
            "submitted": feedback_set[0].datetime.timestamp()
        })
    if download:
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows([[
            "Submitted",
            "Severity",
            "Body",
            "Author",
            "Role",
            "Group"
        ]])
        cw.writerows(
            [
                datetime.fromtimestamp(f["submitted"]),
                f["severity"],
                f["body"],
                f["author"],
                f["role"],
                "{} {}".format(f["color"] or "", f["letter"] or ""),
            ] for f in feedback)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=feedback.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    return jsonify(
        {
            "results": feedback,
            "quantity": len(feedback),
            "year": year
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
        if parameters["color"].lower() == "red" or parameters["response"].lower() == "asap":
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
                            parameters["color"].capitalize(),
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


@feedback_bp.route('/api/feedback/<fid>', methods=["PUT"])
def hide_feedback(fid):
    feedback = Feedback.query.filter(Feedback.id == fid).first()
    if not feedback:
        return jsonify({
            "success": False,
            "error": "Feedback ID not found!"
        })

    feedback.handled = True
    db.session.commit()
    return jsonify({
        "success": True,
    })
