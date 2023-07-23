import json
import os
import tarfile
import zipfile
from os.path import isfile, split, relpath, join


class Archive:
    @staticmethod
    def extract_zip_file(file_name, directory=os.getcwd(), remove=False):
        data = {
            'request': 'extract_zip_file'
        }
        try:
            if zipfile.is_zipfile(join(directory, file_name)):
                status = 200
                data['response'] = {}
                zip_file = zipfile.ZipFile(join(directory, file_name))
                files = zip_file.namelist()
                zip_file.extractall(path=directory)
                zip_file.close()
                if remove:
                    os.remove(join(directory, file_name))
                data['response']['zip_file'] = join(directory, file_name)
                data['response']['extracts'] = []
                for file in files:
                    zip_extract_details = {'file_name': file, 'directory': directory}
                    if isfile(join(directory, file)):
                        zip_extract_details['extracted'] = True
                    else:
                        zip_extract_details['extracted'] = False
                    data['response']['extracts'].append(zip_extract_details)
            else:
                status = 404
                data['response'] = "Zip file not found"
        except Exception as e:
            status = 401
            data['response'] = "Error extracting zip archive : {}".format(str(e))

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    @staticmethod
    def extract_tar_file(file_name, directory=os.getcwd(), remove=False):
        data = {
            'request': 'extract_tar_file'
        }
        try:
            if isfile(join(directory, file_name)) and tarfile.is_tarfile(join(directory, file_name)):
                status = 200
                data['response'] = {}
                tar_file = tarfile.open(join(directory, file_name))
                files = tar_file.getmembers()
                tar_file.extractall(path=directory)
                tar_file.close()
                if remove:
                    os.remove(join(directory, file_name))
                data['response']['tar_file'] = join(directory, file_name)
                data['response']['extracts'] = []
                for file in files:
                    tar_extract_details = {'file_name': file.name, 'directory': directory}
                    if isfile(join(directory, file.name)):
                        tar_extract_details['extracted'] = True
                    else:
                        tar_extract_details['extracted'] = False
                    data['response']['extracts'].append(tar_extract_details)
            else:
                status = 404
                data['response'] = "Tar file not found"
        except Exception as e:
            status = 401
            data['response'] = str(e)

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    @staticmethod
    def create_zip_file(files, zip_file_name, directory=os.getcwd(), remove=False):
        """
        :param files: [
            {
                "file_name": "USTOCK_20190918.002_rrp_rq.pkg",
                "directory": "D:\\PROJECTS\\ops_stack\\_tmp"
            },
            {
                "file_name": "USTOCK_20190918.002_rrp_rs.pkg",
                "directory": "D:\\PROJECTS\\ops_stack\\_tmp"
            }
        ]
        :param zip_file_name: Name of zip file to be created
        :param directory: Directory where Zip file is created
        :param remove: Remove row files after directory
        :return: status, details
        """
        data = {
            'request': 'create_zip_file'
        }
        try:
            status = 200
            zip_file = zipfile.ZipFile(join(directory, zip_file_name), "w", zipfile.ZIP_DEFLATED)
            data['response'] = {'directory': directory, 'zip_file': zip_file_name, 'files': []}
            if not isinstance(files, list):
                files = [files]
            for file in files:
                if isinstance(file, dict):
                    file_name = file['file_name']
                    if 'directory' in file:
                        file_dir = file['directory']
                    else:
                        file_dir = os.getcwd()
                else:
                    file_name = file
                    file_dir = directory
                zip_details = {'file': file_name, 'directory': file_dir}
                if isfile(join(file_dir, file_name)):
                    try:
                        zip_file.write(join(file_dir, file_name), relpath(join(file_dir, file_name), file_dir))
                        zip_details['archived'] = True
                        if remove:
                            os.remove(join(file_dir, file_name))
                    except Exception as e:
                        zip_details['archived'] = False
                        zip_details['error'] = str(e)
                else:
                    zip_details['archived'] = False
                    zip_details['error'] = "File not found"
                data['response']['files'].append(zip_details)
            zip_file.close()
        except Exception as e:
            status = 401
            data['response'] = "Error creating zip archive : {}".format(str(e))

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})

    @staticmethod
    def create_tar_file(files, tar_file_name, directory, tar_type='tar.gz', remove=False):
        """
        :param files: list
        [
            {
                "file_name": "USTOCK_20190918.002_rrp_rq.pkg",
                "directory": "D:\\PROJECTS\\ops_stack\\_tmp"
            },
            {
                "file_name": "USTOCK_20190918.002_rrp_rs.pkg",
                "directory": "D:\\PROJECTS\\ops_stack\\_tmp"
            }
        ]
        :param tar_file_name: Name of zip file to be created
        :param directory:  Directory where Zip file is created
        :param tar_type:
        :param remove: Remove row files after directory
        :return:
        """
        data = {
            'request': 'create_{}_file'.format(tar_type)
        }
        if tar_type in ['tar.gz', 'tgz']:
            try:
                status = 200
                if tar_type.lower() == 'tgz':
                    tar_file = tarfile.open(join(directory, tar_file_name), "w:gz")
                else:
                    tar_file = tarfile.open(join(directory, tar_file_name), "w")
                data['response'] = {'directory': directory, 'tar_file': tar_file_name, 'files': []}
                for file in files:
                    if isinstance(file, dict):
                        file_name = file['file_name']
                        if 'directory' in file:
                            file_dir = file['directory']
                        else:
                            file_dir = os.getcwd()
                    else:
                        file_name = file
                        file_dir = directory
                    tar_details = {'file': file_name, 'directory': file_dir}
                    if isfile(join(file_dir, file_name)):
                        try:
                            tar_file.add(join(file_dir, file_name),
                                         relpath(join(file_dir, file_name), file_dir))
                            tar_details['archived'] = True
                            if remove:
                                os.remove(join(file_dir, file_name))
                        except Exception as e:
                            tar_details['archived'] = False
                            tar_details['error'] = str(e)
                    else:
                        tar_details['archived'] = False
                        tar_details['error'] = "File not found"
                    data['response']['files'].append(tar_details)
                tar_file.close()
            except Exception as e:
                status = 401
                data['response'] = str(e)
        else:
            status = 405
            data['response'] = "Unsupported tar file type {}".format(tar_type)

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data})
