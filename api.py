# -*- coding: utf-8 -*-
from app_factory import create_app

app = create_app()

@app.route('/')
def index():
    return "Welcome to the Magic of ORKG"

if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'])
