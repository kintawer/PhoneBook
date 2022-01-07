from flask import render_template, url_for, flash, request
from werkzeug.urls import url_parse
from werkzeug.utils import redirect

from app import app, db
from flask_login import current_user, login_user, logout_user, login_required

from app.forms import RegistrationForm, LoginForm, SearchUserForm, \
    RelationForm, ChatForm
from app.models import User, Relation, Message


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = SearchUserForm()

    if not form.validate_on_submit():
        return render_template('index.html', title='index', form=form)

    if form.username.data:
        found_user = User.query.filter_by(
            username=form.username.data).first()
    else:
        found_user = User.query.filter_by(
            phone_number=form.phone_number.data).first()

    if found_user:
        return redirect(url_for('user', username=found_user.username))
    else:
        flash('User not found.')

    return redirect(url_for('index'))


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form_relation = RelationForm()
    form_chat = ChatForm()
    user = User.query.filter_by(username=username).first_or_404()
    relation = current_user.get_relation(user)

    if form_relation.submit_rel.data and form_relation.validate():
        if not relation:
            relation = Relation(owner_id=current_user.id, subject_id=user.id)
        if form_relation.username.data:
            relation.username = form_relation.username.data
            form_relation.username.data = None
        if form_relation.note.data:
            relation.note = form_relation.note.data
            form_relation.note.data = None
        db.session.add(relation)
        db.session.commit()
        return redirect(url_for('user', username=user.username))

    if form_chat.validate_on_submit() and form_chat.message.data:
        if not relation:
            relation = Relation(owner_id=current_user.id, subject_id=user.id)
        message = Message(message=form_chat.message.data, relation=relation)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('user', username=user.username))

    page = request.args.get('page', 1, type=int)
    messages = current_user.get_messages(user).paginate(
        page, app.config['MESSAGES_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=messages.next_num)\
        if messages.has_next else None
    prev_url = url_for('user', username=user.username, page=messages.prev_num)\
        if messages.has_prev else None
    return render_template('user.html', user=user, relation=relation,
                           form_relation=form_relation, form_chat=form_chat,
                           next_url=next_url, prev_url=prev_url,
                           messages=messages.items, page=page)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if not form.validate_on_submit():
        return render_template('register.html', title='Register', form=form)

    user = User(username=form.username.data, email=form.email.data,
                phone_number=form.phone_number.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash('Congratulations, you are now a registered user!')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('login.html', title='Sign In', form=form)

    user = User.query.filter_by(username=form.username.data).first()
    if user is None or not user.check_password(form.password.data):
        flash('Invalid username or password')
        return redirect(url_for('login'))
    login_user(user, remember=form.remember_me.data)
    next_page = request.args.get('next')

    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    return redirect(next_page)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))

    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))

    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))

    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))
