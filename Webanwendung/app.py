import datetime
import os
import platform
import random
import shutil
import string
from threading import Thread
import threading
import time
import zipfile
from flask import (Flask, jsonify, render_template, request,
                   send_file, send_from_directory)
from werkzeug.utils import secure_filename
import exiftool
import tempfile
from xml.etree import cElementTree as ET
import fileinput
import sys
from flask_wtf.csrf import CSRFProtect

###
#   gunicorn --bind 0.0.0.0 --threads 2 --timeout 600 app:app
#   pip freeze > requirements.txt
# TODOs:
#   - unterscheidung ob lizens einbauen oder copyright notice mit explicitem opt out ✔️
#   - In azure testen:
#       - Bildgöße und automatischens löschen (führt dies zu problemen) ✔️
#       - Scheduler des cleanup funktioniert? ✔️
#   - Scheduler Cleanup Time überlegen (Täglich usw.) (nur leere Ordner oder nur Ordner mit license.xml löschen) ⭕
###

tmp_path = os.path.join(tempfile.gettempdir(), 'Uploads')

app = Flask(__name__)
csrf = CSRFProtect(app)

app.config['SECRET_KEY'] = 'mysecret'
app.config["SOFTWARE_DOWNLOAD"] = f'{os.path.join(os.path.dirname(__file__))}/static/Software'


@app.after_request
def set_security_headers(response):
    # Set Content-Security-Policy header
    response.headers['Content-Security-Policy'] = ("frame-ancestors 'self';"
                                                   "default-src 'self';"
                                                   "script-src 'self' https://cdnjs.cloudflare.com;"
                                                   "style-src 'self' 'unsafe-inline';"
                                                   "img-src 'self' data:;"
                                                   "connect-src 'self';"
                                                   "frame-src 'self';"
                                                   "font-src 'self';"
                                                   "media-src 'self';"
                                                   "form-action 'self';")
    # Set X-Frame-Options header
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/licenses/permitted-for-training')
def do_train():
    return render_template('./licenses/permitted_for_training.html')


@app.route('/licenses/by')
def by():
    return render_template('./licenses/by.html')


@app.route('/licenses/nc')
def nc():
    return render_template('./licenses/nc.html')


@app.route('/licenses/ng')
def ng():
    return render_template('./licenses/ng.html')


@app.route('/licenses/by-nc')
def by_nc():
    return render_template('./licenses/by_nc.html')


@app.route('/licenses/by-ng')
def by_ng():
    return render_template('./licenses/by_ng.html')


@app.route('/licenses/nc-ng')
def nc_ng():
    return render_template('./licenses/nc_ng.html')


@app.route('/licenses/by-nc-ng')
def by_nc_ng():
    return render_template('./licenses/by_nc_ng.html')


@app.route('/licenses/do-not-train')
def do_not_train():
    return render_template('./licenses/do_not_train.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/licensing-tool', methods=["GET"])
def licensing_tool():
    return render_template('licensing_tool.html')


@app.route('/software', methods=["GET"])
def software():
    if 'Mobile' in request.headers.get('User-Agent'):
        return render_template(
            'software.html',
            mobile=True
        )
    else:
        windows_path = f'{app.config["SOFTWARE_DOWNLOAD"]}/AII_Licensing_Windows.zip'
        linux_path = f'{app.config["SOFTWARE_DOWNLOAD"]}/AII_Licensing_Linux.zip'
        macOS_path = f'{app.config["SOFTWARE_DOWNLOAD"]}/AII_Licensing_macOS.zip'
        windows_zip_size = os.path.getsize(windows_path)
        windows_size_in_mb = round(windows_zip_size / (1024 * 1000), 1)
        linux_zip_size = os.path.getsize(linux_path)
        linux_size_in_mb = round(linux_zip_size / (1024 * 1000), 1)
        macOS_zip_size = os.path.getsize(macOS_path)
        macOS_size_in_mb = round(macOS_zip_size / (1024 * 1000), 1)
        return render_template(
            'software.html',
            windows_size=windows_size_in_mb,
            linux_size=linux_size_in_mb,
            macOS_size=macOS_size_in_mb,
            mobile=False
        )


@app.route('/software/<os>')
def download_file(os):
    if os == 'windows':
        return send_from_directory(app.config["SOFTWARE_DOWNLOAD"], 'AII_Licensing_Windows.zip', as_attachment=True, mimetype='application/zip')
    elif os == 'linux':
        return send_from_directory(app.config["SOFTWARE_DOWNLOAD"], 'AII_Licensing_Linux.zip', as_attachment=True, mimetype='application/zip')
    elif os == 'macOS':
        return send_from_directory(app.config["SOFTWARE_DOWNLOAD"], 'AII_Licensing_macOS.zip', as_attachment=True, mimetype='application/zip')
    else:
        alert_script = """
                    <script>
                    $(document).ready(function(){
                            alert('Something went wrong. Please try again.');
                        });
                    </script>
                """
        return render_template('software.html', additional_content=alert_script)


def delay_delete(delay, path, zip):
    time.sleep(delay)
    if zip:
        if os.path.isdir(path):
            file_path = os.path.join(path, 'Licensed_Images.zip')
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting: {e}")
            try:
                shutil.rmtree(path)
            except:
                pass
    else:
        files = os.listdir(path)
        for file_name in files:
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path) and not file_name.endswith('.zip'):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_name}: {e}")
    return


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'jpe', 'png', 'jng', 'mng', 'tiff', 'tif', 'webp', 'jp2', 'jpf', 'jpm',
                      'heif', 'heic', 'hif', 'gif', 'eps', 'psd', 'avif', 'flif', 'mp4'}
ALLOWED_LICENSE_EXTENSIONS = {'xmp'}


def allowed_file(imagename):
    return '.' in imagename and imagename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_license_file(imagename):
    return '.' in imagename and imagename.rsplit('.', 1)[1].lower() in ALLOWED_LICENSE_EXTENSIONS


def license_create(form):
    folder = ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(10))
    try:
        os.mkdir(tmp_path)
    except:
        pass
    path = os.path.join(tmp_path, folder)
    try:
        os.mkdir(path)
    except:
        pass

    license = 'AII '
    if form.get("license_Group") == '1':
        license += form.get("license")
    else:
        if form.get('allow_Group') == '1':
            if form.get('attribution_Group') == '1':
                license += 'BY'
            if form.get('commercial_Group') == '0':
                if len(license) > 1:
                    license += '-NC'
                else:
                    license += 'NC'
            if form.get('generative_Group') == '0':
                if len(license) > 1:
                    license += '-NG'
                else:
                    license += 'NG'
            if len(license) < 1:
                license += 'Permitted For Training'
        else:
            license += 'Do Not Train'

    condition = ""
    if 'Permitted For Training' not in license and 'Do Not Train' not in license:
        condition = "Training is allowed when:"
        if 'BY' in license:
            condition += " Attribution is given;"
        if 'NC' in license:
            condition += " Use is non-commercial;"
        if 'NG' in license:
            condition += " Use is non-generative;"

    tree = ET.parse(
        f'{os.path.join(os.path.dirname(__file__))}/ExifTool/License.xmp')
    root = tree.getroot()
    root.find(
        './/{http://ns.myname.com/AIContact/1.0/}LicensorName').text = form.get('Creator').strip()
    root.find('.//{http://ns.myname.com/AIContact/1.0/}LicensorEmail').find(
        './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = form.get('Email').strip()
    root.find('.//{http://ns.myname.com/AIContact/1.0/}LicensorURL').find(
        './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = form.get('Contact').strip()
    root.find('.//{http://ns.myname.com/AIContact/1.0/}UserDefinedData').find(
        './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = form.get('UDD').strip()
    root.find('.//{http://ns.myname.com/AILicense/1.0/}LicenseCondition').find(
        './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = condition
    root.find('.//{http://ns.myname.com/AILicense/1.0/}License').find(
        './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = license
    root.find('.//{http://ns.myname.com/AILicense/1.0/}LicenseURL').find(
        './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = f'www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}'

    tree.write(f'{path}/{license}_License.xmp')
    with open(f'{path}/{license}_License.xmp', "a") as f:
        f.write("\n<?xpacket end='w'?>\n")
    with open(f'{path}/{license}_License.xmp', "r+") as f:
        old = f.read()
        f.seek(0)
        f.write("<?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>\n" + old)
    for line in fileinput.input(f'{path}/{license}_License.xmp', inplace=True):
        line = line.replace("ns0", "x")
        line = line.replace("ns2", "AIContact")
        line = line.replace("ns3", "AILicense")
        sys.stdout.write(line)
    return [path, license]


@app.route('/license-picker', methods=["GET", "POST"])
def license_picker():
    if request.method == "POST":
        path = license_create(request.form)
        del_thread = Thread(target=delay_delete,
                            args=(3, path[0], True))
        del_thread.start()
        return send_file(f'{path[0]}/{path[1]}_License.xmp', as_attachment=True)
    return render_template('license_picker.html')


MAX_FILE_SUM = 250 * 1024 * 1024


def check_file_sum(files):
    return len(files) > MAX_FILE_SUM


MAX_FILE_SIZE = 256


def check_file_size(files):
    file_size = sum(file.content_length for file in files)
    return file_size > MAX_FILE_SIZE


@app.route('/license-picker/upload', methods=["POST"])
def license_picker_upload():
    form = request.form
    uploaded_files = request.files.getlist("file")
    if check_file_size(uploaded_files):
        return jsonify({'error': 'You can only upload up to 256 images at a time.'})
    elif check_file_sum(uploaded_files):
        return jsonify({'error': 'You can only upload 250MB of data at a time.'})
    else:
        if request.files['file'].filename != '':
            imagenames = []
            folder = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.digits) for _ in range(10))
            try:
                os.makedirs(tmp_path, exist_ok=True)
            except Exception as e:
                print(e)

            path = os.path.join(tmp_path, folder)
            os.makedirs(path, exist_ok=True)
            email = form.get("Email").strip()
            creator = form.get("Creator").strip()
            contact = form.get("Contact").strip()
            udd = form.get("UDD").strip()
            license = 'AII '
            if form.get("license_Group") == '1':
                license += form.get("license")
            else:
                if form.get('allow_Group') == '1':
                    if form.get('attribution_Group') == '1':
                        license += 'BY'
                    if form.get('commercial_Group') == '0':
                        if len(license) > 1:
                            license += '-NC'
                        else:
                            license += 'NC'
                    if form.get('generative_Group') == '0':
                        if len(license) > 1:
                            license += '-NG'
                        else:
                            license += 'NG'
                    if len(license) < 1:
                        license += 'Permitted For Training'
                else:
                    license += 'Do Not Train'

            condition = ""
            if 'Permitted For Training' not in license and 'Do Not Train' not in license:
                condition = "Training is allowed when:"
                if 'BY' in license:
                    condition += " Attribution is given;"
                if 'NC' in license:
                    condition += " Use is non-commercial;"
                if 'NG' in license:
                    condition += " Use is non-generative;"

            for image in uploaded_files:
                if image.filename.rsplit('.', 1)[0] == '':
                    image.filename = ''.join(random.SystemRandom().choice(
                        string.ascii_uppercase + string.digits) for _ in range(5)) + '.' + image.filename.rsplit('.', 1)[1]
                if image and allowed_file(image.filename):
                    imagename = secure_filename(image.filename)
                    image.save(f'{path}/{imagename}')
                    imagenames.append(imagename)
                else:
                    del_thread = Thread(target=delay_delete,
                                        args=(0, path, True))
                    del_thread.start()
                    return jsonify({'error': f'".{image.filename.rsplit(".", 1)[1]}" - is not an allowed file type. Currently supported file types are: {ALLOWED_EXTENSIONS}'})
            timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            if platform.system() == 'Windows':
                with exiftool.ExifTool(executable=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/exiftool.exe', config_file=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/License.config') as et:
                    if license == 'AII Do Not Train':
                        et.execute(
                            f'-EXIF:Copyright=Do Not Train',
                            f'-IPTC:CopyrightNotice=Do Not Train',
                            f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                            f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                            f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                            f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')
                    else:
                        et.execute(
                            f'-EXIF:Copyright=This work is licensed for AI use under the {license}-License',
                            f'-IPTC:CopyrightNotice=This work is licensed for AI use under the {license}-License',
                            f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                            f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                            f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                            f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')
            else:
                with exiftool.ExifTool(executable=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/Linux/exiftool', config_file=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/License.config') as et:
                    if license == 'AII Do Not Train':
                        et.execute(
                            f'-EXIF:Copyright=Do Not Train',
                            f'-IPTC:CopyrightNotice=Do Not Train',
                            f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                            f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                            f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                            f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')
                    else:
                        et.execute(
                            f'-EXIF:Copyright=This work is licensed for AI use under the {license}-License',
                            f'-IPTC:CopyrightNotice=This work is licensed for AI use under the {license}-License',
                            f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                            f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                            f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                            f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')

            if len(imagenames) != 1:
                zipfolder = zipfile.ZipFile(
                    f'{path}/Licensed_Images.zip', 'w', compression=zipfile.ZIP_STORED)

                for filename in imagenames:
                    zipfolder.write(
                        filename=f'{path}/{filename}', arcname=filename)
                zipfolder.close()
                del_thread = Thread(target=delay_delete,
                                    args=(10, path, True))
                del_thread.start()
                return jsonify({'unique_id': folder, 'single': False})
            else:
                del_thread = Thread(target=delay_delete,
                                    args=(10, path, True))
                del_thread.start()
                return jsonify({'unique_id': folder, 'single': True})


@app.route('/download/<unique_id>/<single>')
def download(unique_id, single):
    path = os.path.join(tmp_path, unique_id)
    # del_thread = Thread(target=delay_delete,
    #                    args=(1, path, True))
    # del_thread.start()
    if single == 'true':
        filename = [filename for filename in os.listdir(
            path) if not filename.endswith('.xmp')]
        return send_from_directory(f'{path}', f'{filename[0]}', as_attachment=True)
    return send_from_directory(f'{path}', 'Licensed_Images.zip', as_attachment=True, mimetype='application/zip')


aiilicenses = ['AII BY', 'AII NC', 'AII NG', 'AII BY-NC', 'AII BY-NG',
               'AII NC-NG', 'AII BY-NC-NG', 'AII Permitted For Training', 'AII Do Not Train']


@app.route('/licensing-tool/upload', methods=["POST"])
def licensing_tool_upload():
    uploaded_files = request.files.getlist("file")
    if check_file_size(uploaded_files):
        return jsonify({'error': 'You can only upload up to 256 images at a time.'})
    elif check_file_sum(uploaded_files):
        return jsonify({'error': 'You can only upload 250MB of data at a time.'})
    else:
        if request.files['file'].filename != '' and request.files['license'].filename != '':
            imagenames = []
            folder = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.digits) for _ in range(10))
            try:
                os.mkdir(tmp_path)
            except:
                pass
            path = os.path.join(tmp_path, folder)
            try:
                os.mkdir(path)
            except:
                pass
            uploaded_license = request.files['license']
            if uploaded_license and allowed_license_file(uploaded_license.filename):
                licensename = secure_filename(uploaded_license.filename)
            uploaded_license.save(f'{path}/{licensename}')

            try:
                tree = ET.parse(f'{path}/{licensename}')
                root = tree.getroot()
                creator = root.find(
                    './/{http://ns.myname.com/AIContact/1.0/}LicensorName').text
                if creator == None:
                    creator = ''
                email = root.find('.//{http://ns.myname.com/AIContact/1.0/}LicensorEmail').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
                if email == None:
                    email = ''
                udd = root.find('.//{http://ns.myname.com/AIContact/1.0/}UserDefinedData').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
                if udd == None:
                    udd = ''
                contact = root.find('.//{http://ns.myname.com/AIContact/1.0/}LicensorURL').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
                if contact == None:
                    contact = ''
                condition = root.find('.//{http://ns.myname.com/AILicense/1.0/}LicenseCondition').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
                license = root.find('.//{http://ns.myname.com/AILicense/1.0/}License').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
                if license not in aiilicenses:
                    raise Exception('Wrong license')
                licenseURL = root.find('.//{http://ns.myname.com/AILicense/1.0/}LicenseURL').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
            except:
                del_thread = Thread(target=delay_delete,
                                    args=(5, path, True))
                del_thread.start()
                return jsonify({'error': 'The xmp file provided does not contain a valid license.'})
                # alert_script = """
                #    <script>
                #        $(document).ready(function(){
                #            alert('The xmp file provided does not contain a valid license.');
                #        });
                #    </script>
                # """
                # return render_template('licensing_tool.html', additional_content=alert_script)
            condition = ""
            if 'Permitted For Training' not in license and 'Do Not Train' not in license:
                condition = "Training is allowed when:"
                if 'BY' in license:
                    condition += " Attribution is given;"
                if 'NC' in license:
                    condition += " Use is non-commercial;"
                if 'NG' in license:
                    condition += " Use is non-generative;"
            for image in uploaded_files:
                if image.filename.rsplit('.', 1)[0] == '':
                    image.filename = ''.join(random.SystemRandom().choice(
                        string.ascii_uppercase + string.digits) for _ in range(5)) + '.' + image.filename.rsplit('.', 1)[1]
                if image and allowed_file(image.filename):
                    imagename = secure_filename(image.filename)
                    image.save(f'{path}/{imagename}')
                    imagenames.append(imagename)
                else:
                    del_thread = Thread(target=delay_delete,
                                        args=(0, path, True))
                    del_thread.start()
                    return jsonify({'error': f'".{image.filename.rsplit(".", 1)[1]}" - is not an allowed file type. Currently supported file types are: {ALLOWED_EXTENSIONS}'})
            timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            if platform.system() == 'Windows':
                with exiftool.ExifTool(executable=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/exiftool.exe', config_file=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/License.config') as et:
                    if license == 'AII Do Not Train':
                        et.execute(
                            f'-EXIF:Copyright=Do Not Train',
                            f'-IPTC:CopyrightNotice=Do Not Train',
                            f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                            f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                            f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                            f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')
                    else:
                        et.execute(
                            f'-EXIF:Copyright=This work is licensed for AI use under the {license}-License',
                            f'-IPTC:CopyrightNotice=This work is licensed for AI use under the {license}-License',
                            f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                            f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                            f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                            f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')
            else:
                with exiftool.ExifTool(executable=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/Linux/exiftool', config_file=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/License.config') as et:
                    if license == 'AII Do Not Train':
                        et.execute(
                            f'-EXIF:Copyright=Do Not Train',
                            f'-IPTC:CopyrightNotice=Do Not Train',
                            f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                            f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                            f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                            f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')
                    else:
                        et.execute(
                            f'-EXIF:Copyright=This work is licensed for AI use under the {license}-License',
                            f'-IPTC:CopyrightNotice=This work is licensed for AI use under the {license}-License',
                            f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                            f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                            f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                            f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')

            if len(imagenames) != 1:
                zipfolder = zipfile.ZipFile(
                    f'{path}/Licensed_Images.zip', 'w', compression=zipfile.ZIP_STORED)

                # zip all the files which are inside the folder
                for filename in imagenames:
                    zipfolder.write(
                        filename=f'{path}/{filename}', arcname=filename)
                zipfolder.close()
                del_thread = Thread(target=delay_delete,
                                    args=(10, path, True))
                del_thread.start()
                return jsonify({'unique_id': folder, 'single': False})
            else:
                del_thread = Thread(target=delay_delete,
                                    args=(10, path, True))
                del_thread.start()
                return jsonify({'unique_id': folder, 'single': True})


if __name__ == '__main__':
    # app.debug = True
    app.run(threaded=True)
