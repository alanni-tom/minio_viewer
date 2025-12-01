# minio_utils.py
from minio import Minio
from minio.error import S3Error


class MinioClientHelper:
    def __init__(self, endpoint, access_key, secret_key, secure=True):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def test_connection(self):
        try:
            self.client.list_buckets()
            return True, "连接成功"
        except Exception as e:
            return False, str(e)

    def list_buckets_and_objects(self, bucket_name=None, prefix=""):
        data = {'buckets': [], 'objects': [], 'prefixes': []}
        try:
            if not bucket_name:
                buckets = self.client.list_buckets()
                data['buckets'] = [{'name': b.name, 'creation_date': b.creation_date} for b in buckets]
            else:
                objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=False)
                for obj in objects:
                    if obj.is_dir:
                        data['prefixes'].append({'name': obj.object_name, 'path': obj.object_name})
                    else:
                        file_ext = obj.object_name.split('.')[-1].lower() if '.' in obj.object_name else 'file'
                        data['objects'].append({
                            'name': obj.object_name.replace(prefix, '', 1),
                            'full_path': obj.object_name,
                            'size': obj.size,
                            'last_modified': obj.last_modified,
                            'extension': file_ext
                        })
        except S3Error as e:
            print(f"MinIO Error: {e}")
        return data

    def get_presigned_url(self, bucket_name, object_name):
        return self.client.get_presigned_url("GET", bucket_name, object_name)
