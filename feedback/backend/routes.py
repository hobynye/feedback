from . import app, db
from .models import Feedback, Volunteer, Role, COLORS
from flask import render_template, request, jsonify
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from datetime import datetime
import io
import re
import csv


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


@app.route('/api/users/import', methods={"POST"})
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
        elif not already_processed and (user["role"], user["color"], user["letter"]) != (role.title, role.color, role.letter):
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
