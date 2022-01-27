from flask import render_template, url_for, flash, request, current_app
from werkzeug.utils import redirect

from app import db
from flask_login import current_user, login_required

from app.main.forms import SearchUserForm, RelationForm, ChatForm
from app.models import User, Relation, Message
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
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
        return redirect(url_for('main.user', username=found_user.username))
    else:
        flash('User not found.')

    return redirect(url_for('main.index'))


@bp.route('/user/<username>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.user', username=user.username))

    if form_chat.validate_on_submit() and form_chat.message.data:
        if not relation:
            relation = Relation(owner_id=current_user.id, subject_id=user.id)
        message = Message(message=form_chat.message.data, relation=relation)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('main.user', username=user.username))

    page = request.args.get('page', 1, type=int)
    messages = current_user.get_messages(user).paginate(
        page, current_app.config['MESSAGES_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=messages.next_num) if messages.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=messages.prev_num) if messages.has_prev else None
    return render_template('user.html', user=user, relation=relation,
                           form_relation=form_relation, form_chat=form_chat,
                           next_url=next_url, prev_url=prev_url,
                           messages=messages.items, page=page)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))

    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))

    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))

    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username=username))
