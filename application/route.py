from application import app, db
from flask import render_template, session, redirect, url_for, flash, request, jsonify
from application.forms import LoginForm, RegistrationForm, AddTutorial
from application.models import User, Tutorial, user_schema, users_schema, tutorial_schema, tutorials_schema
from flask_jwt_extended import create_access_token, jwt_required


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("DB created")


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', index=True)


@app.route('/login', methods=['get', 'post'])
def login():
    if session.get('username'):
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = User.query.filter(User.email == email, User.password == password).first()
        if result:
            flash("You are successfully logged in!", "success")
            session['user_id'] = result.id
            session['username'] = email
            return redirect(url_for("index"))
        else:
            flash("Please register first", "danger")
            return redirect(url_for('register'))
    return render_template('login.html', title='Login', form=form, login=True)


@app.route("/logout")
def logout():
    session['user_id'] = False
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['get', 'post'])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User(email=email, password=password, first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()
        flash("You are successfully registered!", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form, register=True)


@app.route('/tutorials')
def tutorials():
    results = Tutorial.query.all()
    return render_template('tutorials.html', tutorials=results, tutorial=True)


@app.route('/mytutorial')
def mytutorial():
    if not session.get('username'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    user = User.query.filter(User.id == int(user_id)).first()
    tutorials = user.tutorials.all()
    return render_template("enrollment.html", title='Enrollment', tutorials=tutorials, mytutorial=True)


@app.route('/add_tutorial', methods=['POST', 'GET'])
def add_tutorial():
    if not session.get('username'):
        return redirect(url_for('index'))
    form = AddTutorial()

    if form.validate_on_submit():
        name = form.name.data
        result = Tutorial.query.filter(Tutorial.name == name).first()
        if result:
            flash(f"{name} Tutorial already exist", "danger")
        else:
            price = int(form.price.data)
            description = form.description.data
            tutorial = Tutorial(name=name, price=price, description=description)
            print(name)
            db.session.add(tutorial)
            db.session.commit()
            flash(f"New {name} tutorial added", "success")
            return redirect(url_for("tutorials"))
    return render_template("add_tutorial.html", title="New tutorial", form=form, add_tutorial=True)


@app.route('/delete_tutorial', methods=['get', 'post'])
def delete_tutorial():
    if not session.get('username'):
        return redirect(url_for('index'))
    tutorial_id = request.form.get('tutorial_id')
    Tutorial.query.filter(Tutorial.id == int(tutorial_id)).delete()
    db.session.commit()
    return redirect(url_for('tutorials'))


@app.route('/remove_tutorial', methods=['get', 'post'])
def remove_tutorial():
    user_id = session.get('user_id')
    tutorial_id = request.form.get('tutorial_id')
    user = User.query.filter(User.id == int(user_id)).first()
    tutorial = Tutorial.query.filter(Tutorial.id == int(tutorial_id)).first()
    if user:
        user.tutorials.remove(tutorial)
        db.session.commit()
        flash(f"{tutorial.name} tutorial deleted", "success")

    return redirect(url_for('mytutorial'))


@app.route('/enrollment', methods=['get', 'post'])
def enrollment():
    if not session.get('username'):
        flash("Please login first")
        return redirect(url_for('login'))

    tutorial_id = request.form.get('tutorial_id')
    name = request.form.get('name')
    user_id = session.get('user_id')

    tutorial = Tutorial.query.filter(Tutorial.id == int(tutorial_id)).first()

    current_user = User.query.filter(User.id == int(user_id)).first()
    current_user_tutorials = current_user.tutorials.all()
    is_exist = False
    for item in current_user_tutorials:
        if item.id == tutorial.id:
            flash(f"Tutorial {name} already enrolled", "danger")
            is_exist = True

    if not is_exist:
        tutorial.user.append(current_user)
        db.session.commit()
        flash(f"{name} tutorial added your list", "success")

    tutorials = current_user.tutorials.all()
    return render_template("enrollment.html", title='Enrollment', tutorials=tutorials)


#####  Android Api

@app.route('/api/register', methods=['post'])
def api_register():
    email = request.form.get('email')
    result = User.query.filter(User.email == email).first()
    if result:
        return jsonify(message="Email already exist", email=email)
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    user = User(email=email, password=password, first_name=first_name, last_name=last_name)
    db.session.add(user)
    db.session.commit()
    return jsonify(users_schema.dump(user))


@app.route('/api/login', methods=["post"])
def api_login():
    email = request.form.get('email')
    password = request.form.get('password')
    result = User.query.filter(User.email == email, password == password).first()
    if result:
        access_token = create_access_token(identity=email)
        return jsonify(access_token=access_token, email=email)
    else:
        return jsonify(message="User not found", email=email)


@app.route('/api/my_tutorial', methods=['get'])
@jwt_required
def api_may_tutorial():
    user_id = request.form.get('user_id')
    user = User.query.filter(User.id == int(user_id)).first()
    if user:
        tutorials = user.tutorials.all()
        return jsonify(tutorials_schema.dump(tutorials))
    else:
        return jsonify(message="No tutorial added")


@app.route('/api/tutorials', methods=['get'])
@jwt_required
def api_tutorials():
    tutorials = Tutorial.query.all()
    return jsonify(tutorials_schema.dump(tutorials))


@app.route('/api/enrollment', methods=['POST'])
@jwt_required
def api_enrollment():
    user_id = request.form.get('user_id')
    tutorial_id = request.form.get('tutorial_id')
    tutorial = Tutorial.query.filter(Tutorial.id == int(tutorial_id)).first()

    current_user = User.query.filter(User.id == int(user_id)).first()
    current_user_tutorials = current_user.tutorials.all()
    for item in current_user_tutorials:
        if item.id == tutorial.id:
            return jsonify(message="Tutorial Already enrolled")

    tutorial.user.append(current_user)
    db.session.commit()
    return jsonify(message="Tutorial enrolled success", name=tutorial.name)
