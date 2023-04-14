"""
To configure the first route
"""
import base64
import configparser
import json
import logging
import os
import zipfile
from subprocess import Popen, PIPE
from subprocess import check_output
import flask
import requests
import urllib3
from flask import (
    current_app as app,
    send_from_directory,
    request,
    redirect,
    url_for,
    render_template,
    flash, abort, make_response, g, jsonify
)
from flask_oidc import OpenIDConnect
from flask_paginate import Pagination, get_page_args
from urllib3.exceptions import InsecureRequestWarning
from werkzeug.utils import secure_filename
from .models import *

logging.basicConfig(level=logging.DEBUG)
x_config = configparser.ConfigParser()
x_config.read('./project/configurations.cfg')

ALLOWED_EXTENSIONS = {'zip'}

s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'

KEYCLOAK_URI = x_config.get("keycloak", "KEYCLOAK_URI")
LOGOUT_URI = x_config.get("uri", "LOGOUT_URI")
REDIRECT_URI = x_config.get("uri", "REDIRECT_URI")
O_DOMAIN = x_config.get("domain", "O_DOMAIN")
SUPPER_EMAIL = x_config.get("domain", "SUPPER_EMAIL")
API_VER = "/api/v1.0"
http_error_200 = 'Success'
req_session = requests.Session()
req_session.verify = False
urllib3.disable_warnings()
x_headers = {'X-Api-Key': SUPPER_EMAIL}
app_center_headers = {'accept': "application/json", 'X-API-Token': "59abbb100e3aa366952a02cbdf5661e32f781f3e"}

oidc = OpenIDConnect(app=app, credentials_store=flask.session)


def get_shell_script_output_using_communicate(filename):
    session = Popen([filename], stdout=PIPE, stderr=PIPE)
    stdout, stderr = session.communicate()
    if stderr:
        raise Exception("Error " + str(stderr))
    return stdout.decode('utf-8')


def get_shell_script_output_using_check_output(filename):
    stdout = check_output([filename]).decode('utf-8')
    return stdout


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def remove_accents(input_str):
    s = ''
    print(input_str.encode('utf-8'))
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s


def get(url, headers=None):
    try:
        res = req_session.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            return res
    except urllib3.exceptions.HTTPError as e:
        return e


def check_authorize():
    if not oidc.user_loggedin:
        return False
    oidc.get_access_token()
    return True


@app.route('/login', methods=['GET'])
@oidc.require_login
def login():
    if not oidc.user_loggedin:
        return logout()
    return redirect('/')


@app.route('/', methods=["GET", "POST"])
# @oidc.require_login
def index():
    print('Is Login :' + str(oidc.user_loggedin))
    warning_message = ""
    success_message = ""
    password = "123456Aa@"
    is_exists_user = False

    if not check_authorize():
        return redirect(url_for('login'))
    else:
        print(g.oidc_id_token)
        email = str(g.oidc_id_token['email'])
        print(email)
        print(password)
        # get role user_id logged
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        get_role_user_id_logged = get_user_role(user_id_logged)
        print("get_role_user_id_logged is " + get_role_user_id_logged)
        user_name_logged = user_id_logged.replace("@vng.com.vn", "")

        projects = get_all_active_project_user(user_name_logged)
        count_user_own_projects = len(projects)

        # Check user id is exits to add
        is_exists = db.session.query(UserTbl).filter(UserTbl.user_id == email).first()
        if is_exists is None:
            print("Add user " + email)
            if email == "hautp2@vng.com.vn":
                db.session.add(
                    UserTbl(user_id=email, password=password, name=str(email).replace("@vng.com.vn", ""), role="supper",
                            is_active=True, description=None))
            else:
                db.session.add(
                    UserTbl(user_id=email, password=password, name=str(email).replace("@vng.com.vn", ""), role="view",
                            is_active=True, description=None))
            db.session.commit()

        if request.method == 'POST':
            form_project_name = str(request.form['prj_name'])
            form_tc_name = str(request.form['tc_name'])
            form_app_version = str(request.form['app_ver'])
            form_device_name = str(request.form['device_name'])
            form_condition_name = str(request.form['condName'])
            print("form_project_name " + form_project_name)
            print("form_tc_name " + form_tc_name)
            print("form_app_version " + form_app_version)
            print("form_device_name " + form_device_name)
            print("form_condition_name " + form_condition_name)

            if form_project_name == "" \
                    or form_tc_name == "" \
                    or form_app_version == "" \
                    or form_device_name == "" \
                    or form_condition_name == "":
                warning_message = "Please input Project, Testcase, App version, Device " \
                                  "or Precondition"
            else:
                get_device_info_url = request.url_root + API_VER + "/devices/get-info/" + form_device_name
                res_device_info = get(get_device_info_url, headers=x_headers)
                device_status = ''
                for res in res_device_info['data']:
                    device_status = res['device_status']
                if device_status is False:
                    warning_message = "Device is already used by another process"
                else:
                    prj_id = ''
                    tc_id = ''
                    device_id = ''

                    for prj in get_all_project():
                        if form_project_name == prj.prj_name:
                            prj_id = prj.prj_id

                    for tc in get_all_testcase():
                        if form_tc_name == tc.tc_name:
                            tc_id = tc.tc_id

                    for device in get_all_device():
                        if form_device_name == device.device_name:
                            device_id = device.device_id

                    add_running(user_id_logged, prj_id, tc_id, device_id, "Waiting", form_condition_name)
                    data_update = {'device_status': False}
                    update_device(device_id, data_update)

                    # Add running log
                    data_update = {
                        'prj_id': prj_id,
                        'tc_id': tc_id,
                        'device_id': device_id,
                        'running_status': "Waiting",
                        'tc_condition': form_condition_name
                    }
                    add_logs(user_id_logged, data_update, device_id + "_running_add")

        # Pagination
        running_list = []
        for running in get_all_user_running(user_id_logged):
            running_list += [running]
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        total = int(get_total_running())
        total_testcase_running = get_total_testcase_running()
        pagination_running = running_list[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        resp = make_response(render_template('home.html',
                                             user_id_logged_role=get_role_user_id_logged,
                                             projects=projects,
                                             runnings=pagination_running,
                                             conditions=get_all_active_cond("TC"),
                                             count_user_own_projects=count_user_own_projects,
                                             is_exists_user=is_exists_user,
                                             warning_message=warning_message,
                                             success_message=success_message,
                                             total_testcase_running=total_testcase_running,
                                             page=page,
                                             per_page=per_page,
                                             pagination=pagination))
        return resp


@app.route('/logout')
# @oidc.require_login
def logout():
    oidc.logout()
    flask.session.clear()
    return redirect(LOGOUT_URI + REDIRECT_URI)


@app.route('/health', methods=['GET'])
def health_check():
    return 'OK'


@app.route('/oidc_callback')
# @oidc.require_login
def oidc_callback():
    return redirect("/")


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["PROJECTS_TESTING_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """


@app.route("/upload_project", methods=["GET", "POST"])
def upload_project_folder():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit  empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["PROJECTS_TESTING_FOLDER"], filename))
            zip_ref = zipfile.ZipFile(os.path.join(app.config["PROJECTS_TESTING_FOLDER"], filename), 'r')
            zip_ref.extractall(app.config["PROJECTS_TESTING_FOLDER"])
            os.remove(os.path.join(app.config["PROJECTS_TESTING_FOLDER"], filename))
            zip_ref.close()
            # return redirect(url_for('upload_file',
            #                         filename=filename))
    return render_template('upload_project.html')


# @app.route("/run_test")
# def run_test():
#     # response = requests.get('http://192.168.28.135:1338/v1/kv/device1')
#     # if request.method == 'PUT':
#     #         des = request.args.get("des")
#     #         ver = request.args.get("ver")
#     #         url = "http://192.168.28.135:1338/v1/kv/dead-target-tests/test-gun-recommend"
#     #         payload = json.dumps({
#     #             "testcase": "bin/bash test_gun_recommend.sh",
#     #             "description": des,
#     #             "appVer": ver
#     #
#     #         })
#     #         headers = {
#     #             'Content-Type': 'application/json'
#     #         }
#
#     # response = requests.request("PUT", url, headers=headers, data=payload)
#     return render_template('run_test.html')


@app.route('/validate', methods=["POST"])
def validate():
    if request.method == 'POST' and request.form['pass'] == '000':
        return redirect(url_for("success"))
    else:
        abort(401)


@app.route('/add_tc', methods=['POST', 'GET'])
def add_tc():
    if request.method == 'POST':
        prj_name = str(request.form['prj_select'])
        tc_id = str(request.form['tc_select'])
        tc_name = str(request.form['tc_name']).lower().replace(",", "").replace(" ", "-")
        remove_accents(tc_name)
        precondition = str(request.form['precondition'])
        appver = str(request.form['appver_select'])
        print('projects name: ' + prj_name)
        print('testcase id: ' + tc_id)
        print('testcase name: ' + tc_name)
        print('precondition: ' + precondition)
        print('appver: ' + appver)
        # Get check valid testcase
        get_tc_url = "http://192.168.28.135:1338/v1/kv/" + prj_name + "/" + tc_name
        print(get_tc_url)
        response = requests.request("GET", get_tc_url)
        print('response.status_code', str(response.status_code))
        if response.status_code == 200:
            # response_str = response.text
            response_js = response.json()
            res_len = len(response.json())
            res_value = response_js[res_len - 1]['Value']
            print('res_value', res_value)
            if res_value is None or res_value == 'e30=':
                print('Put testcase to consul with res_value is None or res_value == e30=')
                # Put testcase to consul
                put_tc_url = "http://192.168.28.135:1338/v1/kv/" + prj_name + "/" + tc_name
                payload = json.dumps({
                    "testcase": "bin/bash " + tc_id + ".sh",
                    "precondition": precondition,
                    "appVer": appver,
                    "status": "Waiting"
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                requests.request("PUT", put_tc_url, headers=headers, data=payload)
            else:
                res_value_decode = str(base64.b64decode(res_value).decode("utf-8"))
                print('res_value_decode', res_value_decode)
                res_value_json = json.loads(res_value_decode)
                tc_status = res_value_json['status']
                print(tc_status)
                if tc_status == ("Done" or "Cancel"):
                    print('Put testcase to consul with status done')
                    # Put testcase to consul
                    put_tc_url = "http://192.168.28.135:1338/v1/kv/" + prj_name + "/" + tc_name
                    payload = json.dumps({
                        "testcase": "bin/bash " + tc_id + ".sh",
                        "precondition": precondition,
                        "appVer": appver,
                        "status": "Waiting"
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    requests.request("PUT", put_tc_url, headers=headers, data=payload)
        else:
            print('Put testcase to consul with status !200')
            # Put testcase to consul
            put_tc_url = "http://192.168.28.135:1338/v1/kv/" + prj_name + "/" + tc_name
            payload = json.dumps({
                "testcase": "bin/bash " + tc_id + ".sh",
                "precondition": precondition,
                "appVer": appver,
                "status": "Waiting"
            })
            headers = {
                'Content-Type': 'application/json'
            }
            requests.request("PUT", put_tc_url, headers=headers, data=payload)

    resp = make_response(render_template('manage_test.html'))
    return resp


@app.route('/admin')
# @oidc.require_login
def manage_admin():
    print('Is Login :' + str(oidc.user_loggedin))
    if not check_authorize():
        return redirect(url_for('login'))

    if oidc.user_loggedin is True:
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        print(get_user_role(user_id_logged))
        if get_user_role(user_id_logged) == "view":
            return redirect("/")

    # Pagination
    running_list = []
    for running in get_all_running():
        running_list += [running]
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = int(get_total_running())
    total_testcase_running = get_total_testcase_running()
    pagination_running = running_list[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    resp = make_response(
        render_template('admin/home.html',
                        runnings=pagination_running,
                        total_testcase_running=total_testcase_running,
                        page=page,
                        per_page=per_page,
                        pagination=pagination))
    return resp


@app.route('/manage-user', methods=['POST', 'GET'])
# @oidc.require_login
def manage_users():
    print('Is Login :' + str(oidc.user_loggedin))
    warning_message = ""
    success_message = ""
    password = "123456Aa@"

    if not check_authorize():
        return redirect(url_for('login'))

    if oidc.user_loggedin is True:
        print(g.oidc_id_token)
        email = str(g.oidc_id_token['email'])
        print(email)
        print(password)
        # get role user_id logged
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        if get_user_role(user_id_logged) == "view":
            return redirect("/")
        get_role_user_id_logged = get_user_role(user_id_logged)
        print("get_role_user_id_logged is " + get_role_user_id_logged)
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        get_role_user_id_logged = get_user_role(user_id_logged)
        print("get_role_user_id_logged is " + get_role_user_id_logged)

        if request.method == 'POST':
            form_username = str(request.form['username'])
            form_account_status = str(request.form['account_status'])
            form_user_role = str(request.form['user_role'])
            form_user_desc = str(request.form['userDesc'])
            print("form_username " + form_username)
            print("form_account_status " + form_account_status)
            print("form_user_role " + form_user_role)
            print("form_user_desc " + form_user_desc)

            if form_account_status == "active":
                form_account_status = True
            else:
                form_account_status = False

            if user_id_logged == form_username + O_DOMAIN:
                warning_message = "Can't update yourself"
            else:
                # Update user
                data_update = {'is_active': form_account_status, 'role': form_user_role, 'description': form_user_desc}
                update_user(form_username, data_update)
                success_message = "Update success"
                # Add user log
                data_update["user_name"] = form_username
                add_logs(user_id_logged, data_update, form_username + "_user_update")

        # Query

        # Pagination
        user_list = []
        for user in get_all_user():
            user_list += [user]
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        total = int(get_total_user())
        total_active_user = get_total_user("active_user")
        pagination_users = user_list[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        # Response
        resp = make_response(
            render_template('manage_user.html',
                            users=pagination_users,
                            users_limit=get_limit_user(limit=10),
                            user_first=get_first_user(),
                            total_active_user=total_active_user,
                            page=page,
                            per_page=per_page,
                            pagination=pagination,
                            user_id=user_id_logged,
                            user_id_logged_role=get_role_user_id_logged,
                            warning_message=warning_message,
                            success_message=success_message))
        return resp


@app.route('/manage-project', methods=['POST', 'GET'])
# @oidc.require_login
def manage_projects():
    print('Is Login :' + str(oidc.user_loggedin))
    warning_message = ""
    success_message = ""
    member_dict = {"user_id": []}
    member_list = []

    if not check_authorize():
        return redirect(url_for('login'))

    if oidc.user_loggedin is True:
        print(g.oidc_id_token)
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        get_role_user_id_logged = get_user_role(user_id_logged)
        if get_user_role(user_id_logged) == "view":
            return redirect("/")

        if request.method == 'POST':
            form_project_id = str(request.form['prjId'])
            form_project_name = str(request.form['prjName'])
            form_project_member = str(request.form['prjMember'])
            form_project_status = str(request.form['project_status'])
            form_submit_button = str(request.form['submit_button'])
            if form_project_status == "active":
                form_project_status = True
            else:
                form_project_status = False

            member_list = get_project_member(form_project_id)
            print("member_list " + str(member_list))

            if (form_project_id or form_project_name) == "":
                print("form_project_id " + form_project_id)
                print("form_project_name " + form_project_name)
                print("form_project_member " + form_project_member)
                warning_message = "Please input projectId, projectName, projectMember"
            else:
                if form_submit_button == "ADD":
                    if is_exist_prj_id(form_project_id) is None and is_exist_prj_name(form_project_name) is None:
                        print("Add project id " + form_project_id)
                        if form_project_member == "":
                            member_dict["user_id"] += []
                            add_project(form_project_id, form_project_name, form_project_status, member_dict)
                            warning_message = "Add success"
                            # Add project log
                            data_add = {'prj_id': form_project_id, 'prj_name': form_project_name,
                                        'is_active': form_project_status,
                                        'member': {"user_id": form_project_member}}
                            add_logs(user_id_logged, data_add, form_project_id + "_project_add")
                        elif is_exist_user_name(form_project_member) is None:
                            warning_message = "Member isn't exists"
                        else:
                            member_dict["user_id"] += [form_project_member]
                            add_project(form_project_id, form_project_name, form_project_status, member_dict)
                            success_message = "Add success"
                            # Add project log
                            data_update = {'prj_id': form_project_id, 'prj_name': form_project_name,
                                           'is_active': form_project_status,
                                           'member': {"user_id": form_project_member}}
                            add_logs(user_id_logged, data_update, form_project_id + "_project_add")
                    else:
                        warning_message = "Project id or Project name is exists"

                if form_submit_button == "UPDATE":
                    if is_exist_prj_id(form_project_id) is None and is_exist_prj_name(form_project_name) is None:
                        warning_message = "Project id or Project name isn't exists"
                    else:
                        print("Update project id " + form_project_id)
                        if form_project_member == "" or form_project_member is None:
                            member_list += []
                            data_update = {'prj_name': form_project_name, 'is_active': form_project_status,
                                           'member': {"user_id": member_list}}
                            db.session.query(ProjectTbl).filter_by(prj_id=form_project_id).update(data_update)
                            db.session.commit()
                            success_message = "Update success"

                            # Add project log
                            data_update["prj_id"] = form_project_id
                            add_logs(user_id_logged, data_update, form_project_id + "_project_update")
                        elif is_exist_user_name(form_project_member) is None:
                            warning_message = "Member isn't exists"
                        elif form_project_member in member_list:
                            print("Do nothing")
                            # Add project log
                            data_update = {"prj_id": form_project_id, 'prj_name': form_project_name,
                                           'is_active': form_project_status,
                                           'member': {"user_id": form_project_member}}
                            add_logs(user_id_logged, data_update, form_project_id + "_project_update")
                        else:
                            member_list += [form_project_member]
                            data_update = {'prj_name': form_project_name, 'is_active': form_project_status,
                                           'member': {"user_id": member_list}}
                            db.session.query(ProjectTbl).filter_by(prj_id=form_project_id).update(data_update)
                            db.session.commit()
                            success_message = "Update success"

                            # Add project log
                            data_update["prj_id"] = form_project_id
                            add_logs(user_id_logged, data_update, form_project_id + "_project_update")

                if form_submit_button == "DELETE":
                    if is_exist_prj_id(form_project_id) is None and is_exist_prj_name(form_project_name) is None:
                        warning_message = "Project id or Project name isn't exists"
                    else:
                        print("Remove member in " + form_project_id)
                        if form_project_member == "":
                            warning_message = "Please input member need to delist"
                        elif is_exist_user_name(form_project_member) is None:
                            warning_message = "Member isn't exists"
                        elif form_project_member in member_list:
                            member_list.remove(form_project_member)
                            data_update = {'member': {"user_id": member_list}}
                            db.session.query(ProjectTbl).filter_by(prj_id=form_project_id).update(data_update)
                            db.session.commit()
                            success_message = "Delist member success"

                            # Add project log
                            data_update["prj_id"] = form_project_id
                            add_logs(user_id_logged, data_update, form_project_id + "_project_remove_member")
                        else:
                            warning_message = "Member isn't not in project"

        # Query

        # Pagination
        prj_list = []
        for prj in get_all_project():
            prj_list += [prj]
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        total = int(get_total_user())
        pagination_prj = prj_list[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        resp = make_response(render_template('manage_project.html',
                                             projects=pagination_prj,
                                             users=get_all_active_user(),
                                             member_list=member_list,
                                             warning_message=warning_message,
                                             success_message=success_message,
                                             total_active_project=get_total_user("active_user"),
                                             page=page,
                                             per_page=per_page,
                                             pagination=pagination,
                                             user_id=user_id_logged,
                                             user_id_logged_role=get_role_user_id_logged))
        return resp


@app.route('/manage-device', methods=['POST', 'GET'])
# @oidc.require_login
def manage_devices():
    print('Is Login :' + str(oidc.user_loggedin))
    warning_message = ""
    success_message = ""

    if not check_authorize():
        return redirect(url_for('login'))

    if oidc.user_loggedin is True:
        print(g.oidc_id_token)
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        get_role_user_id_logged = get_user_role(user_id_logged)
        if get_user_role(user_id_logged) == "view":
            return redirect("/")

        if request.method == 'POST':
            form_device_id = str(request.form['deviceId'])
            form_project_id = str(request.form['prjId'])
            form_device_name = str(request.form['deviceName'])
            form_device_platform_name = str(request.form['devicePlatformName'])
            form_device_status = str(request.form['device_status'])
            form_device_is_active = str(request.form['device_is_active'])
            form_submit_button = str(request.form['submit_button'])

            print("form_device_id " + form_device_id)
            print("form_project_id " + form_project_id)
            print("form_device_name " + form_device_name)
            print("form_device_platform_name " + form_device_platform_name)
            print("form_device_status " + form_device_status)
            print("form_device_is_active " + form_device_is_active)

            if form_device_status == "online":
                form_device_status = True
            else:
                form_device_status = False

            if form_device_is_active == "active":
                form_device_is_active = True
            else:
                form_device_is_active = False

            if (form_device_id or form_device_name or form_project_id) == "":
                warning_message = "Please input deviceId, form_project_id, deviceName"
            else:
                if form_submit_button == "ADD":
                    if is_exist_prj_id(form_project_id) is None:
                        warning_message = "Project ID isn't exist"
                    elif is_exists_device_id(form_device_id) is None and is_exists_device_name(
                            form_device_name) is None:
                        print("Add device id " + form_device_id)
                        add_device(form_device_id, form_device_name, form_device_platform_name,
                                   form_device_status, form_device_is_active, form_project_id)
                        success_message = "Add success"
                        # Add device log
                        data_update = {'device_id': form_device_id,
                                       'prj_id': form_project_id,
                                       'device_name': form_device_name,
                                       'device_platform_name': form_device_platform_name,
                                       'device_status': form_device_status,
                                       'is_active': form_device_is_active}
                        add_logs(user_id_logged, data_update, form_device_id + "_device_add")
                    else:
                        warning_message = "Device ID or Device Name is exists"

                if form_submit_button == "UPDATE":
                    if is_exist_prj_id(form_project_id) is None \
                            or is_exists_device_id(form_device_id) is None \
                            or is_exists_device_name(form_device_name) is None:
                        warning_message = "Device id ,Device name or Project Id isn't exists"
                    else:
                        print("Update project id " + form_project_id)
                        # Update device
                        data_update = {'device_id': form_device_id,
                                       'prj_id': form_project_id,
                                       'device_name': form_device_name,
                                       'device_platform_name': form_device_platform_name,
                                       'device_status': form_device_status,
                                       'is_active': form_device_is_active}
                        update_device(form_device_id, data_update)
                        success_message = "Update success"

                        # Add user log
                        add_logs(user_id_logged, data_update, form_device_id + "_device_update")

        # Pagination
        device_list = []
        for device in get_all_device():
            device_list += [device]
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        total = int(get_total_device())
        pagination_device = device_list[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        resp = make_response(render_template('manage_device.html',
                                             devices=pagination_device,
                                             projects=get_all_active_project(),
                                             warning_message=warning_message,
                                             success_message=success_message,
                                             total_active_device=get_total_device("active"),
                                             page=page,
                                             per_page=per_page,
                                             pagination=pagination,
                                             user_id_logged=user_id_logged,
                                             user_id_logged_role=get_role_user_id_logged))
        return resp


@app.route('/manage-testcase', methods=['POST', 'GET'])
# @oidc.require_login
def manage_testcases():
    print('Is Login :' + str(oidc.user_loggedin))
    warning_message = ""
    success_message = ""

    if not check_authorize():
        return redirect(url_for('login'))

    if oidc.user_loggedin is True:
        print(g.oidc_id_token)
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        get_role_user_id_logged = get_user_role(user_id_logged)
        if get_user_role(user_id_logged) == "view":
            return redirect("/")

        if request.method == 'POST':
            form_tc_id = str(request.form['tcId'])
            form_project_id = str(request.form['prjId'])
            form_tc_name = str(request.form['tcName'])
            form_tc_description = str(request.form['tcDesc'])
            form_tc_is_active = str(request.form['tc_is_active'])
            form_submit_button = str(request.form['submit_button'])

            print("form_device_id " + form_tc_id)
            print("form_project_id " + form_project_id)
            print("form_tc_name " + form_tc_name)
            print("form_tc_description " + form_tc_description)

            if form_tc_is_active == "active":
                form_tc_is_active = True
            else:
                form_tc_is_active = False

            if (form_tc_id or form_tc_name or form_project_id) == "":
                warning_message = "Please input deviceId, form_project_id, deviceName"
            else:
                if form_submit_button == "ADD":
                    if is_exist_prj_id(form_project_id) is None:
                        warning_message = "Project ID isn't exist"
                    elif is_exists_tc_id(form_tc_id) is None and is_exists_tc_name(
                            form_tc_name) is None:
                        print("Add device id " + form_tc_id)
                        add_testcase(form_tc_id, form_tc_name, form_tc_description, form_tc_is_active, form_project_id)
                        success_message = "Add success"
                        # Add device log
                        data_update = {'tc_id': form_tc_id,
                                       'prj_id': form_project_id,
                                       'tc_name': form_tc_name,
                                       'description': form_tc_description,
                                       'is_active': form_tc_is_active}
                        add_logs(user_id_logged, data_update, form_tc_id + "_testcase_add")
                    else:
                        warning_message = "Testcase ID or Testcase Name is exists"

                if form_submit_button == "UPDATE":
                    if is_exist_prj_id(form_project_id) is None \
                            or is_exists_tc_id(form_tc_id) is None \
                            or is_exists_tc_name(form_tc_name) is None:
                        warning_message = "Testcase id ,Testcase name or Project Id isn't exists"
                    else:
                        print("Update Testcase id " + form_tc_id)
                        # Update device
                        data_update = {'tc_id': form_tc_id,
                                       'prj_id': form_project_id,
                                       'tc_name': form_tc_name,
                                       'description': form_tc_description,
                                       'is_active': form_tc_is_active}
                        update_testcase(form_tc_id, data_update)
                        success_message = "Update success"

                        # Add user log
                        add_logs(user_id_logged, data_update, form_tc_id + "_testcase_update")

        # Pagination
        tc_list = []
        for tc in get_all_testcase():
            tc_list += [tc]
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        total = int(get_total_testcase())
        pagination_tc = tc_list[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        resp = make_response(render_template('manage_testcase.html',
                                             testcases=pagination_tc,
                                             projects=get_all_active_project(),
                                             warning_message=warning_message,
                                             success_message=success_message,
                                             total_active_testcase=get_total_testcase("active"),
                                             page=page,
                                             per_page=per_page,
                                             pagination=pagination,
                                             user_id_logged=user_id_logged,
                                             user_id_logged_role=get_role_user_id_logged))
        return resp


@app.route('/manage-log')
# @oidc.require_login
def manage_log():
    print('Is Login :' + str(oidc.user_loggedin))
    warning_message = ""
    success_message = ""
    if not check_authorize():
        return redirect(url_for('login'))

    if oidc.user_loggedin is True:
        print(g.oidc_id_token)
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        get_role_user_id_logged = get_user_role(user_id_logged)
        if get_user_role(user_id_logged) == "view":
            return redirect("/")

        # Pagination
        log_list = []
        for lg in get_all_logs():
            log_list += [lg]
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        total = int(get_total_logs())
        pagination_lg = log_list[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        resp = make_response(render_template('manage_log.html',
                                             logs=pagination_lg,
                                             warning_message=warning_message,
                                             success_message=success_message,
                                             page=page,
                                             per_page=per_page,
                                             pagination=pagination,
                                             user_id_logged=user_id_logged,
                                             user_id_logged_role=get_role_user_id_logged))
        return resp


@app.route('/manage-condition', methods=['POST', 'GET'])
# @oidc.require_login
def manage_condition():
    print('Is Login :' + str(oidc.user_loggedin))
    warning_message = ""
    success_message = ""

    if not check_authorize():
        return redirect(url_for('login'))

    if oidc.user_loggedin is True:
        print(g.oidc_id_token)
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        if get_user_role(user_id_logged) == "view":
            return redirect("/")

        if request.method == 'POST':
            form_condition_id = str(request.form['condId'])
            form_condition_name = str(request.form['condName'])
            form_condition_group = str(request.form['condGroup'])
            form_condition_is_active = str(request.form['cond_is_active'])
            form_submit_button = str(request.form['submit_button'])

            if form_condition_is_active == "active":
                form_condition_is_active = True
            else:
                form_condition_is_active = False

            if form_condition_name == "" or form_condition_group == "":
                warning_message = "Please input condition"
            else:
                if form_submit_button == "ADD":
                    if is_exist_cond_name(form_condition_name) is None:
                        print("Add condition name " + form_condition_name)
                        print("Add condition group " + form_condition_group)
                        add_cond(form_condition_name, form_condition_group, form_condition_is_active)
                        success_message = "Add success"

                        # Add condition log
                        data_update = {'cond_name': form_condition_name,
                                       'cond_group': form_condition_group,
                                       'is_active': form_condition_is_active,
                                       'cond_id': form_condition_id}
                        add_logs(user_id_logged, data_update, "condition_add")
                    else:
                        warning_message = "Condition already exists"

                if form_submit_button == "UPDATE":
                    print("Update condition name " + form_condition_name)
                    if form_condition_name == "" or form_condition_name is None:
                        warning_message = "Please input condition"
                    else:
                        data_update = {'cond_name': form_condition_name,
                                       'cond_group': form_condition_group,
                                       'is_active': form_condition_is_active}
                        update_cond(form_condition_id, data_update)
                        success_message = "Update success"

                        # update condition log
                        data_update["cond_id"] = form_condition_id
                        add_logs(user_id_logged, data_update, "condition_update")
        # Pagination
        cond_list = []
        for cond in get_all_cond():
            cond_list += [cond]
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        total = int(get_total_cond())
        pagination_prj = cond_list[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        resp = make_response(render_template('manage_condition.html',
                                             conditions=pagination_prj,
                                             warning_message=warning_message,
                                             success_message=success_message,
                                             total_cond=total,
                                             page=page,
                                             per_page=per_page,
                                             pagination=pagination))
        return resp


@app.route('/revoke-token')
def revoke_oidc_token():
    print('Is Login :' + str(oidc.user_loggedin))
    if oidc.user_loggedin is False:
        oidc.logout()
        flask.session.clear()
        return redirect(LOGOUT_URI + REDIRECT_URI)


@app.route('/get-list-tc-name/<prj_name>', methods=["GET"])
@oidc.require_login
def get_list_tc_name(prj_name):
    print('Is Login :' + str(oidc.user_loggedin))
    password = "123456Aa@"
    if oidc.user_loggedin is True:
        print(g.oidc_id_token)
        email = str(g.oidc_id_token['email'])
        print(email)
        print(password)
        # get role user_id logged
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        get_role_user_id_logged = get_user_role(user_id_logged)
        print("get_role_user_id_logged is " + get_role_user_id_logged)

        testcase_project = get_testcase_project(prj_name)
        return jsonify(testcase_project)


@app.route(API_VER + '/devices/update-status/<device_id>', methods=["PUT"])
def set_status_device(device_id):
    headers = request.headers
    auth = headers.get("X-Api-Key")
    if auth == SUPPER_EMAIL:
        if is_exists_device_id(device_id) is not None:
            device_status = request.json['device_status']
            data_update = {'device_id': device_id, 'device_status': device_status}
            update_device(device_id, data_update)
            result = "Update success device " + str(device_id), 200
        else:
            result = "Device not found", 200
    else:
        result = jsonify({"message": "ERROR: Unauthorized"}), 401

    return result


@app.route(API_VER + '/devices/get-info/<device_id>', methods=["GET"])
def get_devices_info(device_id):
    headers = request.headers
    auth = headers.get("X-Api-Key")
    if auth == SUPPER_EMAIL:
        if is_exists_device_id(device_id) is not None:
            device_info = get_device_info(device_id)
            data = {'data': [device.to_dict() for device in device_info]}
            result = jsonify(data), 200
        else:
            result = "Device not found", 200
    else:
        result = jsonify({"message": "ERROR: Unauthorized"}), 401

    return result


@app.route(API_VER + '/devices/get-all', methods=["GET"])
def get_all_devices():
    headers = request.headers
    auth = headers.get("X-Api-Key")
    prj_id = request.args.get('projectId')
    if auth == SUPPER_EMAIL:
        result = jsonify(deviceList=get_list_all_device_project(prj_id)), 200
    else:
        result = jsonify({"message": "ERROR: Unauthorized"}), 401

    return result


@app.route(API_VER + '/running/get-info/<status>', methods=["GET"])
def get_run_info(status):
    headers = request.headers
    auth = headers.get("X-Api-Key")
    if auth == SUPPER_EMAIL:
        running_info = get_running_info(status).all()
        print(running_info)
        if len(running_info) != 0:
            running_info = get_running_info(status)
            data = {'data': [run.to_dict() for run in running_info]}
            result = jsonify(data), 200
        else:
            result = "Test run not found", 200
    else:
        result = jsonify({"message": "ERROR: Unauthorized"}), 401

    return result


@app.route('/get-list-appver', methods=["GET"])
# @oidc.require_login
def get_list_app_version():
    apiUrlBeta = "https://api.appcenter.ms/v0.1/apps/AC-MPS/Dead-Target-Beta-Android/releases?published_only=true&scope=tester"
    apiUrlAlpha = "https://api.appcenter.ms/v0.1/apps/AC-MPS/Dead-Target-Alpha-Android/releases?published_only=true&scope=tester"
    apiUrlUAT = "https://api.appcenter.ms/v0.1/apps/AC-MPS/Dead-Target-UAT-Android/releases?published_only=true&scope=tester"
    listVersionAll = ["beta_latest", "alpha_latest"]
    listVersionBeta = []
    listVersionAlpha = []
    listVersionUAT = []
    print('Is Login :' + str(oidc.user_loggedin))
    password = "123456Aa@"

    if not check_authorize():
        return redirect(url_for('login'))

    if oidc.user_loggedin is True:
        print(g.oidc_id_token)
        email = str(g.oidc_id_token['email'])
        print(email)
        print(password)
        # get role user_id logged
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        get_role_user_id_logged = get_user_role(user_id_logged)
        print("get_role_user_id_logged is " + get_role_user_id_logged)

        # Get appcenter version
        jsonDataBeta = get(apiUrlBeta, headers=app_center_headers)
        jsonDataAlpha = get(apiUrlAlpha, headers=app_center_headers)
        jsonDataUAT = get(apiUrlUAT, headers=app_center_headers)

        # Get apiUrlBeta
        for value in jsonDataBeta:
            listVersionBeta += [value]

        sizeOfListBeta = len(listVersionBeta) - 1

        if sizeOfListBeta < 5:
            for value in range(0, sizeOfListBeta):
                shortVersion = str(listVersionBeta[value]["short_version"])
                longVersion = str(listVersionBeta[value]["version"])
                idVersion = str(listVersionBeta[value]["id"])
                appver = "beta_" + shortVersion + "/" + longVersion + "|" + idVersion
                listVersionAll += [appver]
        else:
            for value in range(0, 5):
                shortVersion = str(listVersionBeta[value]["short_version"])
                longVersion = str(listVersionBeta[value]["version"])
                idVersion = str(listVersionBeta[value]["id"])
                appver = "beta_" + shortVersion + "/" + longVersion + "|" + idVersion
                listVersionAll += [appver]

        # Get apiUrlAlpha
        for value in jsonDataAlpha:
            listVersionAlpha += [value]

        sizeOfListAlpha = len(listVersionAlpha) - 1

        if sizeOfListAlpha < 5:
            for value in range(0, sizeOfListAlpha):
                shortVersion = str(listVersionAlpha[value]["short_version"])
                longVersion = str(listVersionAlpha[value]["version"])
                idVersion = str(listVersionAlpha[value]["id"])
                appver = "alpha_" + shortVersion + "/" + longVersion + "|" + idVersion
                listVersionAll += [appver]
        else:
            for value in range(0, 5):
                shortVersion = str(listVersionAlpha[value]["short_version"])
                longVersion = str(listVersionAlpha[value]["version"])
                idVersion = str(listVersionAlpha[value]["id"])
                appver = "alpha_" + shortVersion + "/" + longVersion + "|" + idVersion
                listVersionAll += [appver]

        # Get apiUrlUAT
        for value in jsonDataUAT:
            listVersionUAT += [value]

        sizeOfListUAT = len(listVersionUAT) - 1

        if sizeOfListUAT < 5:
            for value in range(0, sizeOfListUAT):
                shortVersion = str(listVersionUAT[value]["short_version"])
                longVersion = str(listVersionUAT[value]["version"])
                idVersion = str(listVersionUAT[value]["id"])
                appver = "uat_" + shortVersion + "/" + longVersion + "|" + idVersion
                listVersionAll += [appver]
        else:
            for value in range(0, 5):
                shortVersion = str(listVersionUAT[value]["short_version"])
                longVersion = str(listVersionUAT[value]["version"])
                idVersion = str(listVersionUAT[value]["id"])
                appver = "uat_" + shortVersion + "/" + longVersion + "|" + idVersion
                listVersionAll += [appver]

        return jsonify(listVersionAll)


@app.route(API_VER + '/chat/images/', methods=['POST', 'GET'])
def get_chat_images():
    headers = request.headers
    auth = headers.get("X-Api-Key")
    prj_id = request.args.get('projectId')
    if auth == SUPPER_EMAIL:
        result = jsonify(deviceList=get_list_all_device_project(prj_id)), 200
    else:
        result = jsonify({"message": "ERROR: Unauthorized"}), 401

    return result

#
#
# if __name__ == '__main__':
#     app.run()
