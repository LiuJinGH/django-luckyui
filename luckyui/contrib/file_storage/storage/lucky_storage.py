from datetime import timedelta

from django.core.files.storage import Storage
from minio import Minio
from minio.error import S3Error


class LuckyStorage(Storage):

    def __init__(self, **settings):
        """
        初始化存储对象
        :param settings: option设置的字段
        """
        self._type = settings['type']
        self._bucket = settings['bucket_name']
        self._access_key = settings['access_key']
        self._secret_key = settings['secret_key']
        self._intranet_host = settings['intranet_host']
        self._intranet_ssl = settings['intranet_ssl']
        self._outernet_host = settings['outernet_host']
        self._outernet_ssl = settings['outernet_ssl']

        self._client = Minio(self._intranet_host,
                             access_key=self._access_key,
                             secret_key=self._secret_key,
                             secure=self._intranet_ssl)

    def _open(self, name, mode='rb'):
        """
        在需要打开一个已存储的文件并返回一个可用于读写的文件对象时被调用。
        :param name:
        :param mode:
        :return:
        """

    def _save(self, name, content):
        """
        用于将文件保存到存储后端。这个方法负责处理文件的实际存储过程，包括文件的上传、重命名、以及与存储后端交互的所有细节。
        :param name:
        :param content:
        :return:
        """
        self._client.put_object(self._bucket, name, content, content.size)
        return name

    def delete(self, name):
        """
        删除存储后端的文件。
        :param name:
        :return:
        """

    def exists(self, name):
        """
        检查存储后端是否存在指定的文件。
        :param name:
        :return:
        """
        try:
            self._client.stat_object(self._bucket, name)
            return True
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return False
            raise False

    def listdir(self, path):
        """
        列出存储后端指定路径下的文件和目录。
        :param path:
        :return:
        """

    def size(self, name):
        """
        返回存储后端指定文件名的文件的大小。
        :param name:
        :return:
        """

    def path(self, name):
        """
        返回存储后端指定文件名的文件的系统路径。
        :param name:
        :return:
        """
        return self._bucket + '/' + name

    def url(self, name):
        """
        返回存储后端指定文件名的文件的访问URL。
        :param name:
        :return:
        """

        url = ''
        if self._type == 'MINIO':
            url = self._outernet_host + '/' + self._bucket + '/' + name
            if self._outernet_ssl:
                url = 'https://' + url
            else:
                url = 'http://' + url
        return url
