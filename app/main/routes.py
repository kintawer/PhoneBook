from flask import render_template, url_for, flash, request, current_app
from werkzeug.utils import redirect

from app import db
from flask_login import current_user, login_required

from app.main.forms import SearchUserForm, RelationForm, ChatForm, \
    CreateChatForm, ChangeChatNameForm
from app.models import User, Relation, Message, Chat
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form_search_contact = SearchUserForm()

    # Форма поиска контакта
    if form_search_contact.validate_on_submit():
        if form_search_contact.username.data:
            found_user = User.query.filter_by(
                username=form_search_contact.username.data).first()
        else:
            found_user = User.query.filter_by(
                phone_number=form_search_contact.phone_number.data).first()
        if found_user:
            return redirect(url_for('main.user', username=found_user.username))
        else:
            flash('User not found.')
        return redirect(url_for('main.index'))

    return render_template('index.html', title='index',
                           form_search_contact=form_search_contact)


@bp.route('/group_chat/<chat_name>', methods=['GET', 'POST'])
@login_required
def group_chat(chat_name):
    if chat_name == 'creating_chat':
        chat = None
        potential_user = [followed.username for followed in
                          current_user.followed.all()]
        form_create_chat = CreateChatForm(
            choices=potential_user)
    else:
        form_chat = ChatForm()
        chat = Chat.query.filter_by(name=chat_name).first_or_404()
        potential_user = []
        form_change_chat_name = ChangeChatNameForm()
        for followed in current_user.followed.all():
            if followed not in chat.users.all():
                potential_user.append(followed.username)
        form_create_chat = CreateChatForm(
            choices=potential_user)

    # Создание чата
    if form_create_chat.validate_on_submit() and form_create_chat.users.data\
            and chat_name == 'creating_chat':
        users = [User.query.filter_by(username=username).first() for username
                 in form_create_chat.users.data]
        users.append(current_user)
        new_chat_name = current_user.username
        for new_user in form_create_chat.users.data:
            new_chat_name += '-' + new_user
        chat = Chat(users=users, name=new_chat_name)
        db.session.add(chat)
        db.session.commit()
        return redirect(url_for('main.group_chat', chat_name=chat.name))

    # Добавление участников в чат
    if form_create_chat.validate_on_submit() \
            and form_create_chat.users.data:
        if chat_name == '-'.join([str(x.username) for x in chat.users.all()]):
            switch_name = True
        else:
            switch_name = False
        chat.users.extend([User.query.filter_by(username=username).first()
                           for username in form_create_chat.users.data])
        if switch_name:
            chat.name = '-'.join([str(x.username) for x in chat.users.all()])
        db.session.add(chat)
        db.session.commit()
        return redirect(url_for('main.group_chat', chat_name=chat.name))

    # Смена названия чата
    if chat_name != 'creating_chat' and \
            form_change_chat_name.validate_on_submit() and\
            form_change_chat_name.new_name.data:
        chat.name = form_change_chat_name.new_name.data
        db.session.add(chat)
        db.session.commit()
        return redirect(url_for('main.group_chat', chat_name=chat.name))

    # Форма отправки сообщения
    if chat_name != 'creating_chat' \
            and form_chat.validate_on_submit()\
            and form_chat.message.data:
        message = Message(message=form_chat.message.data, chat=chat,
                          user=current_user)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('main.group_chat', chat_name=chat.name))

    # Отображение чата
    if chat_name != 'creating_chat':
        page = request.args.get('page', 1, type=int)
        messages = chat.messages.order_by(Message.date.desc()).paginate(
            page, current_app.config['MESSAGES_PER_PAGE'], False)
        next_url = url_for('main.group_chat', chat_name=chat_name,
                           page=messages.next_num) if messages.has_next else None
        prev_url = url_for('main.group_chat', chat_name=chat_name,
                           page=messages.prev_num) if messages.has_prev else None
        return render_template('group_chat.html', form_chat=form_chat,
                               form_change_chat_name=form_change_chat_name,
                               next_url=next_url, prev_url=prev_url,
                               messages=reversed(messages.items), page=page,
                               form_create_chat=form_create_chat)

    return render_template('group_chat.html',
                           form_create_chat=form_create_chat)


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form_relation = RelationForm()
    form_chat = ChatForm()
    user = User.query.filter_by(username=username).first_or_404()
    relation = current_user.get_relation(user)
    chat = current_user.get_chat_with(user)

    # Форма добавления информации о контакте
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

    # Форма отправки сообщения
    if form_chat.validate_on_submit() and form_chat.message.data:
        if not chat:
            chat = Chat(users=[current_user, user],
                        name=f'{current_user.username}-{user.username}')
            db.session.add(chat)
        message = Message(message=form_chat.message.data, chat=chat,
                          user=current_user)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('main.user', username=user.username))

    # Отображение страницы
    if not chat:
        return render_template('user.html', user=user, relation=relation,
                               form_relation=form_relation,
                               form_chat=form_chat, messages=None)
    page = request.args.get('page', 1, type=int)
    messages = chat.messages.order_by(Message.date.desc()).paginate(
        page, current_app.config['MESSAGES_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=messages.next_num) if messages.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=messages.prev_num) if messages.has_prev else None
    return render_template('user.html', user=user, relation=relation,
                           form_relation=form_relation, form_chat=form_chat,
                           next_url=next_url, prev_url=prev_url,
                           messages=reversed(messages.items), page=page)


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

