from . import app, db, twilio
from .models import Feedback, Volunteer, Role, COLORS
from .utils import send_mail
from flask import request, jsonify, redirect
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError
from bcrypt import hashpw, gensalt
from datetime import datetime
import urllib.parse
import random
import string
import io
import re
import csv


@app.route('/api/feedback', methods={"GET"})
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


@app.route('/api/feedback', methods={"POST"})
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


@app.route('/api/users', methods={"GET"})
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


@app.route("/api/admin/users", methods=["GET"])
@login_required
def get_all_users():
    year = request.args.get('year', False) or datetime.now().year
    volunteers = Role.query \
        .filter(Role.year == year) \
        .join(Volunteer, Role.volunteer == Volunteer.id) \
        .with_entities(
        Volunteer.id,
        Volunteer.name,
        Volunteer.admin,
        Volunteer.email,
        Volunteer.phone,
        Volunteer.alert,
        Role.color,
        Role.letter,
        Role.title
    )
    all_users = [{
        "id": user.id,
        "name": user.name,
        "admin": user.admin,
        "alert": user.alert,
        "email": user.email,
        "phone": user.phone,
        "color": user.color,
        "letter": user.letter,
        "title": user.title
    } for user in volunteers]

    return jsonify({
        "users": all_users,
        "year": year,
        "count": len(all_users),
        "success": True
    })


@app.route("/api/admin/user/<uid>", methods=["GET"])
@login_required
def get_user(uid=False):
    year = request.args.get('year', False) or datetime.now().year
    if not uid:
        return jsonify({
            "success": False,
            "error": "No 'id' provided."
        })

    volunteer = Role.query \
        .filter(Role.year == year, Volunteer.id == uid) \
        .join(Volunteer, Role.volunteer == Volunteer.id) \
        .with_entities(
        Volunteer.id,
        Volunteer.name,
        Volunteer.admin,
        Volunteer.email,
        Volunteer.phone,
        Role.color,
        Role.letter,
        Role.title
    ).first()
    if volunteer:
        user = {
            "id": volunteer.id,
            "name": volunteer.name,
            "admin": volunteer.admin,
            "email": volunteer.email,
            "phone": volunteer.phone,
            "color": volunteer.color,
            "letter": volunteer.letter,
            "title": volunteer.title
        }

        return jsonify({
            "user": user,
            "year": year,
            "success": True
        })
    return jsonify({
        "success": False,
        "error": "No user found!"
    })


@app.route('/api/admin/users/create', methods={"POST"})
@login_required
def create_user():
    parameters = request.get_json(force=True)
    required = ["name", "email", "title"]
    for field in required:
        if field not in parameters:
            return jsonify({
                "success": False,
                "error": "Missing {} field.".format(field)
            }), 400
    exists = Volunteer.query.filter(Volunteer.name == parameters["name"]).first()
    if exists:
        return jsonify({
            "success": False,
            "error": "User already exists with that name! {}".format(exists)
        })
    role_fields = ["title", "color", "letter"]
    phone = None
    if "phone" in parameters:
        regex = re.compile(r'\+?[2-9]?\d?\d?-?\(?\d{3}\)?[ -]?\d{3}-?\d{4}')
        match = regex.search(parameters["phone"])
        if match:
            canonical_phone = re.sub(r'\D', '', match.group(0))
            phone = canonical_phone[-10:]
    new_user = Volunteer(
        parameters["name"],
        parameters["email"],
        phone
    )
    db.session.add(new_user)
    db.session.commit()
    volunteer = Volunteer.query.filter(Volunteer.name == parameters["name"]).first()
    new_role = Role(
        year=datetime.now().year,
        volunteer=volunteer.id,
        title=parameters["title"]
    )
    for field in role_fields:
        setattr(new_role, field, parameters.get(field, None))
    db.session.add(new_role)
    db.session.commit()
    return jsonify({
        "success": True
    })


@app.route('/api/admin/users/import', methods={"POST"})
@login_required
def mass_import_users():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file"}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({"success": False, "error": "No file"}), 400
    if file.filename.rsplit('.', 1)[1].lower() == "csv":
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
    else:
        return jsonify({"success": False, "error": "File must be a CSV"}), 400

    parsed_count = 0
    user_list = []
    for entry in csv_input:
        # Skip the title row
        if parsed_count == 0:
            parsed_count += 1
            continue
        # Skip pending positions
        empty_values = ["TBA", "TBD", "", " "]
        if entry[0].strip() in empty_values:
            continue

        new_user = {
            "name": "",
            "role": "",
            "color": None,
            "letter": None,
            "phone": None,
            "email": None
        }

        new_user["name"] = "{} {}".format(entry[0].strip(), entry[1].strip())
        new_user["role"] = entry[2]
        if entry[3] in COLORS:
            new_user["color"] = entry[3]
        if len(entry[4]) <= 3 and entry[4] != "LSC":
            new_user["letter"] = entry[4]

        regex = re.compile(r'\+?[2-9]?\d?\d?-?\(?\d{3}\)?[ -]?\d{3}-?\d{4}')
        match = regex.search(entry[5])
        if match:
            canonical_phone = re.sub(r'\D', '', match.group(0))
            new_user["phone"] = canonical_phone[-10:]
        new_user["email"] = str(entry[6]).lower()
        user_list.append(new_user)
        parsed_count += 1

    all_names = [volunteer.name for volunteer in Volunteer.query.all()]
    # Keep track of all of the users we add.
    users_added = []
    for user in user_list:
        if user["name"] not in all_names:
            user_add = Volunteer(name=user["name"], email=user["email"], phone=user["phone"])
            db.session.add(user_add)
            users_added.append(user)
        db.session.commit()

    assigned_roles = {}
    already_processed = []
    for user in user_list:
        volunteer = Volunteer.query.filter(Volunteer.name == user["name"]).first()
        role = Role.query.filter(Role.year == datetime.now().year, Role.volunteer == volunteer.id).first()
        if not role and not already_processed:
            # New volunteer that needs to be added.
            role_add = Role(
                year=datetime.now().year, volunteer=volunteer.id, title=user["role"],
                color=user["color"], letter=user["letter"])
            db.session.add(role_add)
        elif not already_processed and (user["role"], user["color"], user["letter"]) != (
                role.title, role.color, role.letter):
            # Changing the role of an existing volunteer
            role.title = user["role"]
            role.color = user["color"]
            role.letter = user["letter"]
        else:
            # We have already processed this, someone can't have two titles.
            continue

        assigned_roles[user["name"]] = {"role": user["role"], "color": user["color"], "letter": user["letter"]}
        already_processed.append(volunteer.id)

    db.session.commit()
    return jsonify({"results": {"new_users": users_added, "new_roles": assigned_roles}})


@app.route("/api/login", methods={"POST"})
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


@app.route('/api/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route("/api/user/self", methods={"GET"})
@login_required
def get_self():
    return jsonify({
        "success": True,
        "current_user": {
            "name": current_user.name,
            "id": current_user.id
        }
    })


@app.route("/api/admin/user/<uid>", methods=["DELETE"])
@login_required
def delete_user(uid=False):
    if not uid:
        return jsonify({
            "success": False,
            "error": "No 'id' provided."
        }), 400
    Role.query.filter(Role.volunteer == uid).delete()
    Feedback.query.filter(Feedback.submitted_by == uid).delete()
    Volunteer.query.filter(Volunteer.id == uid).delete()
    db.session.commit()
    return jsonify({"success": True})


def generate_passwd(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


@app.route("/api/admin/user/<uid>", methods=["PUT"])
@login_required
def update_user(uid=False):
    if not uid:
        return jsonify({
            "success": False,
            "error": "No 'id' provided."
        }), 400
    parameters = request.get_json(force=True)
    user = Volunteer.query.filter(Volunteer.id == uid).one()
    acceptable = ["name", "email", "phone", "alert", "admin", "color", "letter", "title"]
    for field in parameters:
        if field in acceptable:
            if field == "phone":
                regex = re.compile(r'\+?[2-9]?\d?\d?-?\(?\d{3}\)?[ -]?\d{3}-?\d{4}')
                match = regex.search(parameters["phone"])
                if match:
                    canonical_phone = re.sub(r'\D', '', match.group(0))
                    setattr(user, "phone", canonical_phone[-10:])
            else:
                setattr(user, field, parameters[field])
    if not parameters["admin"]:
        user.alert = False
    elif not user.password:
        password = generate_passwd()
        user.password = hashpw(password.encode("utf-8"), gensalt())
        send_mail(user.email, password)

    db.session.commit()
    return jsonify({"success": True})
