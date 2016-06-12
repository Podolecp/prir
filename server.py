#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import Flask
from flask_restful import Resource, Api, reqparse
import itertools
import string
import os
import hashlib

MAXIMUM_RANGE = 5
HASHALG = 'md5'
PORT = os.getenv('PRIR_SERVER_PORT', '5991')

app = Flask(__name__)
api = Api(app)

class Ping(Resource):
    def get(self):
        return 'pong'


class Server(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('first', type=str, help='pierwszy znak sprawdzanego ciągu')
        self.parser.add_argument('hash', type=str, help='łamany ciąg znaków')
        self.parser.add_argument('chars', type=str, help='występujące ciągi znaków')
        self.parser.add_argument('range', type=int, help='maksymalna długość sprawdzanych słów')

    def post(self):
        "W argumentach zapytania podaje się star, stop i kodowanie"
        args = self.parser.parse_args()
        print ('ARGS:', args)

        if not args['hash']:
            return 'Empty hash argument'
        if not args['chars']:
            args['chars'] = string.ascii_letters + string.digits + string.punctuation
            print(u'Ustawiono domyślny chars')

        if not args['first']:
            args['first'] = string.ascii_letters + string.digits + string.punctuation
            print(u'Ustawiono domyślny first')

        if not args['range']:
            args['range'] = MAXIMUM_RANGE
            print(u'Ustawiono domyślny range')

        password = ''
        for first in args['first']:
            password = first
            print(password)
            if args['hash'] == hashlib.new(HASHALG, password).hexdigest():
                return password
        
        for deep in xrange(1, args['range']):
            gen = itertools.combinations_with_replacement(args['chars'], deep)
            for suffix in gen:
                suffix =''.join(suffix)
                for first in args['first']:
                    password = first + suffix
                    print(password)
                    if args['hash'] == hashlib.new(HASHALG, password).hexdigest():
                        return password
        return None


        for deep in xrange(1, args['range']):
            for first in args['first']:
                prefix = first
                gen = itertools.combinations_with_replacement(args['chars'], deep-1)
                if deep > 1:
                    for suffix in gen:
                        password = prefix
                        for part in suffix:
                            password += part
                            print(password)
                        if password == hashlib.new(HASHALG, password).hexdigest():
                            return password
                else:
                    password = prefix
                    print(password)
                    if password == hashlib.new(HASHALG, password).hexdigest():
                        return password

api.add_resource(Server, '/')
api.add_resource(Ping, '/ping')

if __name__ == '__main__':
    app.run(port=PORT)
