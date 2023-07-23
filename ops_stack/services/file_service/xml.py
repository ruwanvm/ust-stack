import json
import os
import xml.etree.ElementTree as ElementTree
from os.path import join, isfile
from collections import defaultdict


class XmlFile:
    @staticmethod
    def reader(file_name, directory=os.getcwd()):
        data = {
            'request': 'xml_reader'
        }
        xml_data = ""
        if isfile(join(directory, file_name)):
            try:
                tree = ElementTree.parse(join(directory, file_name))
                status = 200
                data['response'] = "xml file read success"
                xml_data = tree.getroot()
            except Exception as e:
                status = 500
                data['response'] = str(e)
        else:
            status = 404
            data['response'] = "File not found"

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'

        return status, json.dumps({'status': status_detail, 'data': data}), xml_data

    @staticmethod
    def writer(xml_data, file_name, directory=os.getcwd()):
        data = {
            'request': 'xml_writer'
        }
        xml_data.write(join(directory, file_name), xml_declaration=True, encoding='utf-8', method="xml")
        try:
            xml_data.write(join(directory, file_name), xml_declaration=True, encoding='utf-8', method="xml")
            status = 200
            data['response'] = {'file': join(directory, file_name), 'xml_created': True}
        except Exception as e:
            status = 504
            data['response'] = {'file': join(directory, file_name), 'xml_created': False, 'error': str(e)}

        if status == 200:
            status_detail = 'success'
        else:
            status_detail = 'fail'
        return status, json.dumps({'status': status_detail, 'data': data})

    @staticmethod
    def to_json(xml_data):
        d = {xml_data.tag: {} if xml_data.attrib else None}
        children = list(xml_data)
        if children:
            dd = defaultdict(list)
            for dc in map(XmlFile.to_json, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {xml_data.tag: {k: v[0] if len(v) == 1 else v
                                for k, v in dd.items()}}
        if xml_data.attrib:
            d[xml_data.tag].update(('@' + k, v)
                                   for k, v in xml_data.attrib.items())
        if xml_data.text:
            text = xml_data.text.strip()
            if children or xml_data.attrib:
                if text:
                    d[xml_data.tag]['#text'] = text
            else:
                d[xml_data.tag] = text
        return d
