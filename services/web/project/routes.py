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
    if not check_authorize():
        return redirect(url_for('login'))
    else:
        print(g.oidc_id_token)
        email = str(g.oidc_id_token['email'])
        print(email)
        # get role user_id logged
        user_id_logged = str(g.oidc_id_token['email'])
        print(user_id_logged)
        get_role_user_id_logged = get_user_role(user_id_logged)
        print("get_role_user_id_logged is " + get_role_user_id_logged)

        # Check user id is exits to add
        is_exists = db.session.query(UserTbl).filter(UserTbl.user_id == email).first()
        if is_exists is None:
            print("Add user " + email)
            if email == "hautp2@vng.com.vn":
                db.session.add(
                    UserTbl(user_id=email, password="", name=str(email).replace("@vng.com.vn", ""), role="supper",
                            is_active=True, description=None))
            else:
                db.session.add(
                    UserTbl(user_id=email, password="", name=str(email).replace("@vng.com.vn", ""), role="view",
                            is_active=True, description=None))
            db.session.commit()

        if request.method == 'POST':
            for file in request.files.getlist('file'):
                file.save(os.path.join(app.config['TESTCASE_FOLDER'], file.filename))
            return render_template("home.html", msg="Files uploaded successfully.")

        return render_template("home.html", msg="")


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


@app.route('/validate', methods=["POST"])
def validate():
    if request.method == 'POST' and request.form['pass'] == '000':
        return redirect(url_for("success"))
    else:
        abort(401)


@app.route('/revoke-token')
def revoke_oidc_token():
    print('Is Login :' + str(oidc.user_loggedin))
    if oidc.user_loggedin is False:
        oidc.logout()
        flask.session.clear()
        return redirect(LOGOUT_URI + REDIRECT_URI)


@app.route(API_VER + '/chat/images/', methods=['POST', 'GET'])
def get_chat_images():
    headers = request.headers
    auth = headers.get("X-Api-Key")
    if auth == SUPPER_EMAIL:
        result = jsonify(deviceList=[""]), 200
    else:
        result = jsonify({"message": "ERROR: Unauthorized"}), 401

    return result