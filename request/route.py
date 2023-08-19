import os
from string import Template
from flask import Blueprint, request, render_template, current_app, redirect, url_for
from db_work import select
from sql_provider import SQLProvider


blueprint_request = Blueprint('bp_request', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_request.route('/', methods=['GET', 'POST'])
def start_request():
    if request.method == 'GET':
        return render_template('menu_request.html', requests_dict=current_app.config['requests_dict'])
    else:
        request_id = request.form['select_request']
        request_info = current_app.config['requests_dict'][request_id]

        if len(request_info['sql']) == 0:
            _sql = provider.get(request_id + '.sql')
            prod_result, schema = select(current_app.config['db_config'], _sql)
            return render_template('db_result.html', schema=schema, result=prod_result,
                                   page_details=request_info['html'])

        else:
            current_app.config['dynamic_params'] = request_id
            return redirect(url_for('bp_request.parameters'))


@blueprint_request.route('/parameters', methods=['GET', 'POST'])
def parameters():
    request_id = current_app.config['dynamic_params']
    request_info = current_app.config['requests_dict'][request_id]
    if request.method == 'GET':
        return render_template('param_form.html', requests_dict=request_info)
    else:
        input_params = {param[0]: request.form.get(param[0]) for param in request_info['sql'].items()}
        page_details = request_info['html']
        page_details['caption'] = Template(page_details['caption']).substitute(**input_params)

        _sql = provider.get(request_id+'.sql', **input_params)
        prod_result, schema = select(current_app.config['db_config'], _sql)
        return render_template('db_result.html', schema=schema, result=prod_result, page_details=page_details)
