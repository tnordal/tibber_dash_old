import dash
from  flask_sqlalchemy import SQLAlchemy
# from db import models, execute_db

app = dash.Dash(__name__,)
server = app.server
app.config.suppress_callback_exceptions = True
