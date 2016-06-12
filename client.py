#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

from flask import Flask
from flask_restful import Resource, Api
import hashlib
import os
import argparse
import requests
import string
import math
import thread

HASHALG = "md5"
PORT = os.getenv('PRIR_CLIENT_PORT', '5990')

app = Flask(__name__)
api = Api(app)

parser = argparse.ArgumentParser()
parser.add_argument('--passw')
parser.add_argument('--hash')
parser.add_argument('--chars')
parser.add_argument('--range')

"""
class Client(Resource):
    def get(self, hash_str):
        hosts = open('hosts.cfg', 'r').split('\n')
        servers = []
        for host in hosts:
            pass
"""


class HashGenerator(Resource):
    def get(self, password):
        return hashlib.new(HASHALG, password).hexdigest()

api.add_resource(HashGenerator, '/hash/<string:password>')

def break_hash(link, data):
    print(requests.post(link, data=data).text)

if __name__ == '__main__':
    args = parser.parse_args()
    print('ARGS:', args)
    if args.passw:
        print(hashlib.new(HASHALG, args.passw).hexdigest())
    if args.hash:
        hosts_list = open('hosts.cfg', 'r').read().split('\n')
        servers = []
        for host in hosts_list:
            if host:
                print('HOST:', host)
                try:
                    response = requests.get('http://{}/ping'.format(host)).text
                    if "pong" in response:
                        print('HOST: OK')
                        servers.append(host)
                except Exception as e:
                    print('HOST: {} jest nieosiągalny. '.format(host), e)
        if not args.chars:
            args.chars = string.ascii_letters + string.punctuation + string.digits
        if not args.range:
            args.range = 5

        step = int(math.ceil(float(len(args.chars))/len(servers)))
        print('STEP:', step)
        for inst in range(len(servers)):
            print('DATA_RANGE:', args.chars[step*inst:step*(inst+1)])
            data={
                    'hash': args.hash,
                    'first': args.chars[step*inst:step*(inst+1)], 
                    'chars': args.chars,
                    'range': args.range
            }
            thread.start_new_thread(
                    break_hash,
                    ('http://' + servers[inst], data)
            )
            """
            import multiprocessing
            pool = multiprocessing.Pool(len(servers))
            pool.apply_async(
                    requests.post,
                    args=('http://' + servers[inst], data),
                    callback=get_response)
            # requests.post('http://' + servers[inst], data=data)
            # do_work(pool)
            pool.close()
            pool.join()
            """

        
    app.run(port=PORT)
