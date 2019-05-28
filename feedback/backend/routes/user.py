from datetime import datetime
import urllib.parse

from bcrypt import hashpw
from flask import Blueprint, request, jsonify, redirect
from flask_login import login_user, logout_user, current_user, login_required

from feedback.backend.models import Role, Volunteer

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/api/users', methods={"GET"})
def list_volunteers():
    admin_only = bool(request.args.get('admin', False) == "true")
    if admin_only:
        volunteers = Role.query \
            .filter(Role.year == datetime.now().year, Volunteer.admin == True) \
            .join(Volunteer, Role.volunteer == Volunteer.id) \
            .with_entities(Volunteer.id, Volunteer.name)
    else:
        volunteers = Role.query \
            .filter(Role.year == datetime.now().year) \
            .join(Volunteer, Role.volunteer == Volunteer.id) \
            .with_entities(Volunteer.id, Volunteer.name)
    return jsonify(
        {
            "volunteers": [{
                "id": row.id,
                "name": row.name
            } for row in volunteers]
        }
    )


@user_bp.route("/api/login", methods={"POST"})
def login():
    user_info = request.get_json(force=True)
    req_params = ["volunteer_id", "password", "next"]
    for param in req_params:
        if param not in user_info:
            return jsonify(
                {
                    "success": False,
                    "error": "No value '{}' value provided.".format(param)
                }
            ), 400
    volunteer = Volunteer.query.filter(Volunteer.id == user_info["volunteer_id"]).first()
    if volunteer.password:
        enc_entered = user_info["password"].encode("utf-8")
        enc_stored = volunteer.password.encode("utf-8")
        # hashpw will return the same hash using the stored salt
        if hashpw(enc_entered, enc_stored) == enc_stored:
            login_user(volunteer, remember=True)
            return jsonify({
                "success": True,
                "next": urllib.parse.unquote(user_info["next"])
            })
        else:
            return jsonify({
                "success": False,
                "error": "Password did not match!"
            }), 400
    else:
        return jsonify({
            "success": False,
            "error": "User does not have a password set."
        }), 400


@user_bp.route('/api/logout')
def logout():
    logout_user()
    return redirect("/")


@user_bp.route("/api/user/self", methods={"GET"})
@login_required
def get_self():
    return jsonify({
        "success": True,
        "current_user": {
            "name": current_user.name,
            "id": current_user.id
        }
    })
