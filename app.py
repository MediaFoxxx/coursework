import os
import json
from flask import Flask, render_template, session, redirect, url_for
from access import login_required, group_required

from auth.route import blueprint_auth
from request.route import blueprint_request
from basket.route import blueprint_order
from report.route import blueprint_report

app = Flask(__name__)
app.secret_key = 'U will never guess it.'

app.register_blueprint(blueprint_auth, url_prefix='/auth')
app.register_blueprint(blueprint_request, url_prefix='/request')
app.register_blueprint(blueprint_order, url_prefix='/order')
app.register_blueprint(blueprint_report, url_prefix='/report')


for file in os.listdir('data_files/config'):
    if file.endswith('.json'):
        with open(f'data_files/config/{file}', 'r', encoding='utf-8') as f:
            app.config[file.replace('.json', '')] = json.load(f)


@app.route('/', methods=['GET', 'POST'])
def main_menu():
    if 'user_id' in session:
        if session.get('user_group', None):
            return render_template('internal_user_menu.html')
        else:
            return render_template('external_user_menu.html')
    else:
        return redirect(url_for('bp_auth.start_auth'))


@app.route('/exit')
def exit_():
    if 'user_id' in session:
        session.clear()
    return render_template('exit.html')


def add_blueprint_access_handler(app, blueprint_names, handler):
    for view_func_name, view_func in app.view_functions.items():    # Цикл по всем доступным обработчикам
        # Имя функции, Сама функция
        view_func_parts = view_func_name.split('.')
        if len(view_func_parts) > 1:
            view_blueprint = view_func_parts[0]     # Имя blueprint
            if view_blueprint in blueprint_names:
                view_func = handler(view_func)  # Функция оборачивается в декоратор
                app.view_functions[view_func_name] = view_func
    return app


if __name__ == '__main__':
    app = add_blueprint_access_handler(app, ['bp_request', 'bp_report', 'bp_order'], group_required)
    app = add_blueprint_access_handler(app, ['bp_request', 'bp_report', 'bp_order'], login_required)
    app.run(host='127.0.0.1', port=5000, debug=True)
