from app import db, create_app
from app.models import User, Relation, Message, Chat

from config import Config


app = create_app(Config)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Relation': Relation,
            'Message': Message, 'Chat': Chat}
