from functools import wraps
from flask import session, render_template, request, current_app


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        return render_template('access_refused.html')
    return wrapper


def group_validation(config):
    endpoint_func = request.endpoint    # bp_request.start_request
    endpoint_app = request.endpoint.split('.')[0]   # bp_request

    if endpoint_func == 'bp_request.parameters':
        request_name = current_app.config['dynamic_params']
        endpoint_func = endpoint_app + '.' + request_name

    # if 'user_group' in session:     # Если internal user
    user_group = session['user_group']
    if user_group is None:
        user_group = 'external'

    if user_group in config:
        if endpoint_func in config[user_group] or endpoint_app in config[user_group]:  # config = access_config.json
            return True
    return False


def group_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        config = current_app.config['access_config']
        if group_validation(config):
            return f(*args, **kwargs)
        return render_template('access_denied.html')
    return wrapper
