#!/usr/bin/env python3
"""
Flask app with Babel, timezone and current time display
"""

from flask import Flask, render_template, request, g
from flask_babel import Babel
import pytz
from datetime import datetime

app = Flask(__name__)
babel = Babel(app)

users = {
    1: {"name": "Balou", "locale": "fr", "timezone": "Europe/Paris"},
    2: {"name": "Beyonce", "locale": "en", "timezone": "US/Central"},
    3: {"name": "Spock", "locale": "kg", "timezone": "Vulcan"},
    4: {"name": "Teletubby", "locale": None, "timezone": "Europe/London"},
}


class Config:
    """Config class to set default languages and timezone."""
    LANGUAGES = ["en", "fr"]
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"


app.config.from_object(Config)


def get_user():
    """Retrieve user based on ID passed in URL."""
    user_id = request.args.get('login_as')
    if user_id and int(user_id) in users:
        return users[int(user_id)]
    return None


@app.before_request
def before_request():
    """Set user globally if logged in."""
    g.user = get_user()


@babel.localeselector
def get_locale():
    """Determine the best match for supported languages."""
    locale = request.args.get('locale')
    if locale in app.config['LANGUAGES']:
        return locale
    if g.user and g.user['locale'] in app.config['LANGUAGES']:
        return g.user['locale']
    return request.accept_languages.best_match(app.config['LANGUAGES'])


@babel.timezoneselector
def get_timezone():
    """Determine the best match for the user's timezone."""
    timezone = request.args.get('timezone')
    if timezone:
        try:
            return pytz.timezone(timezone).zone
        except pytz.exceptions.UnknownTimeZoneError:
            pass
    if g.user and g.user['timezone']:
        try:
            return pytz.timezone(g.user['timezone']).zone
        except pytz.exceptions.UnknownTimeZoneError:
            pass
    return app.config['BABEL_DEFAULT_TIMEZONE']


def get_current_time_in_timezone(timezone_str):
    """Return the current time in the specified timezone."""
    try:
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    except pytz.exceptions.UnknownTimeZoneError:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@app.route('/')
def index():
    """Route to render the home page."""
    current_time = get_current_time_in_timezone(get_timezone())
    return render_template('7-index.html', current_time=current_time)


if __name__ == '__main__':
    app.run(debug=True)
