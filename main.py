from app.models import User, Relation, Message
from app import app, db


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Relation': Relation, 'Message': Message}
