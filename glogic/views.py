from . import app
from .import bot_view, careers_view


@app.route('/', methods=['GET', 'POST'])
def root():
    return "I'm working"
