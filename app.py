import os
import io
import zipfile
from datetime import timedelta
from flask import Flask, render_template, request, session, redirect, url_for, send_file, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from minio import Minio
from minio.error import S3Error

app = Flask(__name__)

# 自行修改
app.secret_key = 'minio_viewer'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=7)

db = SQLAlchemy(app)


class MinioConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(200), nullable=False)
    access_key = db.Column(db.String(200), nullable=False)
    secret_key = db.Column(db.String(200), nullable=False)
    secure = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()


def get_minio_client():
    if 'minio_config' not in session:
        return None
    conf = session['minio_config']
    try:
        client = Minio(
            conf['endpoint'],
            access_key=conf['access_key'],
            secret_key=conf['secret_key'],
            secure=conf['secure']
        )
        return client
    except:
        return None


def get_file_icon(filename):
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    icons = {
        'pdf': 'fa-file-pdf text-red-500',
        'jpg': 'fa-file-image text-purple-500', 'jpeg': 'fa-file-image text-purple-500',
        'png': 'fa-file-image text-purple-500',
        'txt': 'fa-file-alt text-gray-500', 'md': 'fa-file-code text-blue-500',
        'zip': 'fa-file-archive text-yellow-600', 'rar': 'fa-file-archive text-yellow-600',
        'py': 'fa-file-code text-green-500', 'js': 'fa-file-code text-yellow-400',
        'mp4': 'fa-file-video text-pink-500', 'mp3': 'fa-file-audio text-indigo-500'
    }
    return icons.get(ext, 'fa-file text-gray-400')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        endpoint = request.form.get('endpoint')
        ak = request.form.get('access_key')
        sk = request.form.get('secret_key')
        alias = request.form.get('alias', endpoint)
        secure = request.form.get('secure') == 'on'
        save_info = request.form.get('save_info') == 'on'

        try:
            client = Minio(endpoint, access_key=ak, secret_key=sk, secure=secure)
            client.list_buckets()

            session['minio_config'] = {
                'endpoint': endpoint, 'access_key': ak, 'secret_key': sk, 'secure': secure
            }
            session.permanent = True

            if save_info:
                exists = MinioConfig.query.filter_by(endpoint=endpoint, access_key=ak).first()
                if not exists:
                    new_conf = MinioConfig(alias=alias, endpoint=endpoint, access_key=ak, secret_key=sk, secure=secure)
                    db.session.add(new_conf)
                    db.session.commit()

            return redirect(url_for('browser'))
        except Exception as e:
            flash(f"连接失败: {str(e)}", "error")

    saved_conns = MinioConfig.query.all()
    return render_template('index.html', saved_conns=saved_conns)


@app.route('/load_config/<int:id>')
def load_config(id):
    conf = MinioConfig.query.get_or_404(id)
    session['minio_config'] = {
        'endpoint': conf.endpoint, 'access_key': conf.access_key, 'secret_key': conf.secret_key, 'secure': conf.secure
    }
    return redirect(url_for('browser'))


@app.route('/delete_config/<int:id>')
def delete_config(id):
    conf = MinioConfig.query.get_or_404(id)
    db.session.delete(conf)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('minio_config', None)
    return redirect(url_for('index'))


@app.route('/browser/')
@app.route('/browser/<bucket_name>/')
@app.route('/browser/<bucket_name>/<path:prefix>')
def browser(bucket_name=None, prefix=""):
    client = get_minio_client()
    if not client:
        return redirect(url_for('index'))

    if prefix and not prefix.endswith('/'):
        prefix += '/'

    data = {'buckets': [], 'objects': [], 'folders': []}

    try:
        if not bucket_name:
            buckets = client.list_buckets()
            data['buckets'] = buckets
        else:
            objects = client.list_objects(bucket_name, prefix=prefix, recursive=False)
            for obj in objects:
                if obj.is_dir:
                    data['folders'].append(obj.object_name)
                else:
                    url = client.get_presigned_url("GET", bucket_name, obj.object_name, expires=timedelta(hours=1))
                    data['objects'].append({
                        'name': obj.object_name.replace(prefix, ''),
                        'path': obj.object_name,
                        'size': obj.size,
                        'last_modified': obj.last_modified,
                        'icon': get_file_icon(obj.object_name),
                        'url': url,
                        'is_image': obj.object_name.lower().endswith(('.jpg', '.png', '.jpeg', '.gif'))
                    })
    except S3Error as e:
        flash(f"MinIO 错误: {e}", "error")

    breadcrumbs = []
    if bucket_name:
        breadcrumbs.append({'name': bucket_name, 'url': url_for('browser', bucket_name=bucket_name)})
        parts = prefix.strip('/').split('/')
        built_path = ""
        for part in parts:
            if part:
                built_path += part + "/"
                breadcrumbs.append(
                    {'name': part, 'url': url_for('browser', bucket_name=bucket_name, prefix=built_path)})

    return render_template('browser.html', data=data, bucket=bucket_name, prefix=prefix, breadcrumbs=breadcrumbs)


@app.route('/upload', methods=['POST'])
def upload():
    client = get_minio_client()
    bucket_name = request.form.get('bucket_name')
    prefix = request.form.get('prefix', '')

    if not client or not bucket_name:
        flash("上传失败：连接丢失或参数错误", "error")
        return redirect(url_for('index'))

    if 'file' not in request.files:
        flash("未选择文件", "error")
        return redirect(url_for('browser', bucket_name=bucket_name, prefix=prefix))

    file = request.files['file']
    if file.filename == '':
        flash("文件名不能为空", "error")
        return redirect(url_for('browser', bucket_name=bucket_name, prefix=prefix))

    try:
        file_data = file.read()
        file_size = len(file_data)
        file_stream = io.BytesIO(file_data)

        object_name = prefix + file.filename

        client.put_object(
            bucket_name,
            object_name,
            file_stream,
            file_size,
            content_type=file.content_type
        )
        flash(f"文件 {file.filename} 上传成功", "success")
    except S3Error as e:
        flash(f"MinIO 上传错误: {e}", "error")
    except Exception as e:
        flash(f"系统错误: {e}", "error")

    return redirect(url_for('browser', bucket_name=bucket_name, prefix=prefix))


@app.route('/create_folder', methods=['POST'])
def create_folder():
    client = get_minio_client()
    bucket_name = request.form.get('bucket_name')
    prefix = request.form.get('prefix', '')
    folder_name = request.form.get('folder_name', '').strip()

    if not folder_name:
        flash("文件夹名称不能为空", "error")
        return redirect(url_for('browser', bucket_name=bucket_name, prefix=prefix))

    folder_name = folder_name.strip('/')

    object_name = f"{prefix}{folder_name}/"

    try:
        client.put_object(
            bucket_name,
            object_name,
            io.BytesIO(b''),
            0
        )
        flash(f"文件夹 {folder_name} 创建成功", "success")
    except Exception as e:
        flash(f"创建失败: {e}", "error")

    return redirect(url_for('browser', bucket_name=bucket_name, prefix=prefix))


@app.route('/download/<bucket_name>/<path:filepath>')
def download_file(bucket_name, filepath):
    client = get_minio_client()
    try:
        response = client.get_object(bucket_name, filepath)
        return send_file(
            io.BytesIO(response.read()),
            as_attachment=True,
            download_name=filepath.split('/')[-1]
        )
    except Exception as e:
        return str(e)


@app.route('/download_all/<bucket_name>/')
@app.route('/download_all/<bucket_name>/<path:prefix>')
def download_all(bucket_name, prefix=""):
    client = get_minio_client()
    if prefix and not prefix.endswith('/'):
        prefix += '/'

    try:
        objects = client.list_objects(bucket_name, prefix=prefix, recursive=True)

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for obj in objects:
                if not obj.is_dir:
                    file_data = client.get_object(bucket_name, obj.object_name)
                    arcname = obj.object_name[len(prefix):]
                    zf.writestr(arcname, file_data.read())

        memory_file.seek(0)
        zip_name = f"{prefix.strip('/').split('/')[-1] or bucket_name}.zip"

        return send_file(memory_file, download_name=zip_name, as_attachment=True)
    except Exception as e:
        return f"打包下载失败: {str(e)}"


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
