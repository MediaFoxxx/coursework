import os
from string import Template
from flask import Blueprint, request, render_template, current_app, redirect, url_for
from coursework.db_work import call_proc, select
from coursework.sql_provider import SQLProvider


blueprint_report = Blueprint('bp_report', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_report.route('/', methods=['GET', 'POST'])
def start_report():
    if request.method == 'GET':
        return render_template('menu_report.html', report_list=current_app.config['reports_dict'])
    else:
        rep_id = request.form.get('rep_id')
        if request.form.get('create_rep'):
            url_rep = current_app.config['reports_dict'][rep_id]['create_rep']
        else:
            url_rep = current_app.config['reports_dict'][rep_id]['view_rep']
        return redirect(url_for(url_rep))


@blueprint_report.route('/create_rep', methods=['GET', 'POST'])
def create_rep():
    report_info = current_app.config['reports_dict']['bouquets_report']
    if request.method == 'GET':
        return render_template('param_form_rep.html', report_info=report_info)
    else:
        # input_params = {param[0]: request.form.get(param[0]) for param in report_info['report'].items()}
        input_params = [request.form.get(param[0]) for param in report_info['report'].items()]
        call_proc(current_app.config['db_config'], 'bouquetsreport', input_params)

        return render_template('created_report.html')

        # request_info = current_app.config['reports_dict']['bouquets_report']
        # _sql = provider.get('bouquets_report_create.sql', i_year=input_params[0], i_month=input_params[1])
        # prod_result, schema = select(current_app.config['db_config'], _sql)
        #
        # return render_template('db_result_rep.html', schema=schema, result=prod_result,
        #                        page_details=request_info['html'])


@blueprint_report.route('/view_rep', methods=['GET', 'POST'])
def view_rep():
    report_info = current_app.config['reports_dict']['bouquets_report']
    if request.method == 'GET':
        return render_template('param_form_rep.html', report_info=report_info)
    else:
        # input_params = {param[0]: request.form.get(param[0]) for param in report_info['report'].items()}
        i_year = request.form.get('year')
        i_month = request.form.get('month')

        if i_month and i_year:
            _sql = provider.get('find_report.sql', i_year=i_year, i_month=i_month)
            prod_result, schema = select(current_app.config['db_config'], _sql)
            if len(prod_result) > 0:
                caption = Template(report_info['html']['caption']).substitute(year=i_year, month=i_month)
                return render_template('db_result_rep.html', schema=schema, result=prod_result,
                                       page_details=report_info['html'], caption=caption)
            else:
                return render_template('param_form_rep.html', report_info=report_info,
                                       message='Отчет по заданным параметрам не создан!')
        else:
            return render_template('param_form_rep.html', report_info=report_info, message='Введите параметры запроса!')
