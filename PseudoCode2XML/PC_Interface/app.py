from __future__ import absolute_import
from pprint import pprint
import os
from flask import Flask, render_template, request, session, abort, flash, url_for, send_file
from detect_intent_texts import detect_intent_texts
from read_attributes import get_columns
from werkzeug.utils import secure_filename, redirect
from API_manager import enter_new_entity, enter_filename_entity
import DB_Manager

app = Flask(__name__)

app.secret_key = "AS9UjjJI0J0JS9j"

PROJECT_ID = os.getenv('GCLOUD_PROJECT')
SESSION_ID = 'fake_session_for_testing'
# UPLOAD_FOLDER = '/home/madusha/'
UPLOAD_FOLDER = '/media/madusha/DA0838CA0838A781/PC_Interface/Resources'
ALLOWED_EXTENSIONS = set(['csv', 'txt'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
url_ds_attributes = 'https://api.dialogflow.com/v1/entities/ds_attributes'
url_ds_name = 'https://api.dialogflow.com/v1/entities/Dataset_Name'


@app.route('/payload', methods=['POST'])
def payload():
    if not request.json:
        abort(400)
    if request.json:
        response = request.json
        pprint(response)

    try:
        content = request.json['queryResult']
        print("_" * 20)
        pprint(content)

    except:
        print("JSON not found")

    return 'none'


def test_detect_intent_texts(capsys):
    detect_intent_texts(PROJECT_ID, SESSION_ID, TEXTS, 'en-US')
    out, _ = capsys.readouterr()

    assert 'Fulfillment text: All set!' in out


@app.route('/send_message', methods=['POST'])
def send_message():
    message = "Hi, Name please"
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = {"message": fulfillment_text}
    print(response_text)


@app.route('/')
def home():
    return render_template('home.html')


@app.route("/find/<string:name>/")
def hello(name):
    return render_template('found_wim_phone.html', name=name)


@app.route('/home', methods=['GET'])
def search():
    try:
        phone_price = request.form['price']

        users = findUsersByPrice(phone_price)
        return render_template('home.html', ph_price=phone_price, users_list=users)
    except:
        return render_template('home.html')


@app.route('/pc', methods=['GET'])
def receive_pseudo_code():
    try:
        pseudocode = request.form['pcode']
        lines = pseudocode.split('\n')
        DB_Manager.insert_pseudocode_into_db(lines)
        # print(lines)
        # detect_intent_texts(PROJECT_ID, SESSION_ID, lines, 'en-US')

        # return render_template('result1.html')
        return render_template('result1.html', statements=lines)
    except:
        return render_template('input_form1.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/ds', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            columns = get_columns(UPLOAD_FOLDER + '/' + filename)
            print(columns)
            enter_filename_entity([filename], url_ds_name)
            enter_new_entity(columns, url_ds_attributes)
            return render_template('pseudocode_input.html', filename=filename)
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
    return render_template('input_form1.html')


@app.route('/intermediate', methods=['GET', 'POST'])
def generate_intermediate_code():
    lines = DB_Manager.get_pseudocode_from_db()[0]
    full_pc = ""
    for line in lines:
        pc = detect_intent_texts(PROJECT_ID, SESSION_ID, [line], 'en-US')
        full_pc = full_pc + '\n' + pc

    print(full_pc)
    # f = open(os.path.join(app.config['DOWNLOAD_FOLDER']) + '/ipc.txt', "w+")
    f = open("ipc.txt", "w+")
    f.write(full_pc)
    DB_Manager.delete_all_documents("pseudocodes_temp")
    # path = "ipc.txt"
    # return send_file(path, as_attachment=True)
    return render_template('result1.html', statements=lines)


@app.route('/sc', methods=['GET'])
def generate_source_code():
    try:
        pseudocode = request.form['pcode']
        # chipset = request.form['cs']

        # phones = RecommendOnChipset(chipset)
        print(pseudocode)
        return render_template('result2.html', name=user_name, phone_cs_list=set(phones))
    except:
        return render_template('input_form2.html')


@app.route('/evl', methods=['GET'])
def evaluate_results():
    try:
        user_name = request.form['username']
        agegroup = request.form['age']
        phones = teenPhone(agegroup)
        print(phones)

        return render_template('result3.html', name=user_name, phone_age_list=phones)
    except:
        return render_template('input_form3.html')


@app.route('/about', methods=['GET'])
def about():
    try:
        user_name = request.form['username']
        brand_name = request.form['brandname']
        os = request.form['os']

        return render_template('result4.html', name=user_name)
    except:
        return render_template('input_form4.html')


app.add_url_rule('/pc', 'pc', receive_pseudo_code, methods=['GET', 'POST'])
app.add_url_rule('/ds', 'ds', upload_file, methods=['GET', 'POST'])
app.add_url_rule('/intermediate', 'intermediate', generate_intermediate_code, methods=['GET', 'POST'])
app.add_url_rule('/sc', 'sc', generate_source_code, methods=['GET', 'POST'])
app.add_url_rule('/eval', 'eval', evaluate_results, methods=['GET', 'POST'])
app.add_url_rule('/about', 'about', about, methods=['GET', 'POST'])

if __name__ == "__main__":
    app.run(host='localhost', port=3550, debug=True)
