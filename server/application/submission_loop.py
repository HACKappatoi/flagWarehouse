import logging
import time
from datetime import datetime, timedelta
from queue import Queue
import json

import requests
from flask import Flask, current_app
from ordered_set import OrderedSet

from . import db

from pwnlib.tubes.remote import remote
import urllib.parse

class OrderedSetQueue(Queue):
    """Unique queue.

    Elements cannot be repeated, so there's no need to traverse it to check.
    LIFO ordered and thread-safe.
    """

    def _init(self, maxsize):
        self.queue = OrderedSet()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()



class Submitter:
    FAUST_TY  = 'faust'
    CCIT_TY   = 'ccit'
    ENOWAR_TY = 'enowar'
    HTTP_C_TY = 'custom-nc'
    NC_C_TY   = 'custom-http'
    
    CUSTOM_SUBMITTER_FUNCTION = None
    
    SUB_ACCEPTED      = 'accepted'
    SUB_INVALID       = 'invalid'
    SUB_OLD           = 'too old'
    SUB_YOUR_OWN      = 'your own'
    SUB_STOLEN        = 'already stolen'
    SUB_NOP           = 'from NOP team'
    SUB_NOT_AVAILABLE = 'is not available'

    def netcat_submitter(self, flags):
        try:
            print(f' {self.host} {self.port}')
            sub = remote(self.host, self.port, timeout=current_app.config['SUB_TIMEOUT'])
            
            while sub.recv(1,timeout=1):
                continue
            res = []
            for flag in flags:
                sub.sendline(flag.encode())
                sub_res = sub.recvlineS().split()
                
                if len(sub_res) < 1 or sub_res[0] not in flags:
                    print(f'[_netcat_submitter]: {sub_res}')
                    continue
                res.append({'flag':sub_res[0], 'msg':sub_line[1]})
            return res
        
        except Exception as ex:
            print(ex)
            return []
    
    def http_submitter(self, flags):
        res = requests.put(current_app.config['SUB_URL'],
                            headers={'X-Team-Token': current_app.config['TEAM_TOKEN']},
                            json=flags,
                            timeout=(current_app.config['SUB_INTERVAL'] / current_app.config['SUB_LIMIT']))

        # Check if the gameserver sent a response about the flags or if it sent an error
        if res.headers['Content-Type'] == 'application/json; charset=utf-8':
            return json.loads(res.text)
        else:
            current_app.logger.error(f'Received this response from the gameserver:\n\n{res.text}\n')
            return []  
      
    def __init__(self, app_configs, sub_type, sub_fun=None ,keywords={}):
        sub_type_implemented = [self.FAUST_TY, self.CCIT_TY, self.ENOWAR_TY, self.HTTP_C_TY, self.NC_C_TY]
        self.keywords = keywords
        self.CUSTOM_SUBMITTER_FUNCTION = sub_fun
        if sub_type not in sub_type_implemented:
            raise NotImplementedError()
        
        # init submitter data
        url = urllib.parse.urlsplit(app_configs['SUB_URL'])
        self.host = url.hostname
        self.port = url.port
        print(f'{self.host}, {self.port}') 
        
        if sub_type == self.FAUST_TY:
            # init submitter keywords
            self.SUB_ACCEPTED      = 'OK'
            self.SUB_INVALID       = 'INV'
            self.SUB_OLD           = 'OLD'
            self.SUB_YOUR_OWN      = 'OWN'
            self.SUB_STOLEN        = 'DUP'
            self.SUB_NOP           = 'INV'
            self.SUB_NOT_AVAILABLE = 'ERR'  
            
            # select submit function
            self.submit_fn = self.netcat_submitter
        
        elif sub_type == self.CCIT_TY:
            # init submitter keywords
            self.SUB_ACCEPTED      = 'accepted'
            self.SUB_INVALID       = 'invalid'
            self.SUB_OLD           = 'too old'
            self.SUB_YOUR_OWN      = 'your own'
            self.SUB_STOLEN        = 'already stolen'
            self.SUB_NOP           = 'from NOP team'
            self.SUB_NOT_AVAILABLE = 'is not available'
            
            # select submit function
            self.submit_fn = self.http_submitter
            
            
        elif sub_type == self.ENOWAR_TY:
            # init submitter keywords
            self.SUB_ACCEPTED      = 'OK'
            self.SUB_INVALID       = 'INV'
            self.SUB_OLD           = 'OLD'
            self.SUB_YOUR_OWN      = 'OWN'
            self.SUB_STOLEN        = 'DUP'
            self.SUB_NOP           = 'INV'
            self.SUB_NOT_AVAILABLE = 'ERR'
            # select submit function
            self.submit_fn = self.netcat_submitter
            
        elif sub_type == self.NC_C_TY or ub_type == self.HTTP_C_TY:
            # init submitter keywords
            self.SUB_ACCEPTED      = self.keywords['SUB_ACCEPTED']
            self.SUB_INVALID       = self.keywords['SUB_INVALID']
            self.SUB_OLD           = self.keywords['SUB_OLD']
            self.SUB_YOUR_OWN      = self.keywords['SUB_YOUR_OWN']
            self.SUB_STOLEN        = self.keywords['SUB_STOLEN']
            self.SUB_NOP           = self.keywords['SUB_NOP']
            self.SUB_NOT_AVAILABLE = self.keywords['SUB_NOT_AVAILABLE']
            
            # select submit function
            self.submit_fn = self.CUSTOM_SUBMITTER_FUNCTION
            if self.CUSTOM_SUBMITTER_FUNCTION is not None:
                print(f'submitter_name {self.submit_fn.__name__}')
                return 
            	
            self.submit_fn = self.http_submitter
            if sub_type == self.NC_C_TY:
                self.submit_fn = self.netcat_submitter
        
        print(f'submitter_name {self.submit_fn.__name__}')
            
    def submit(self, flags):
        print('STO SUB')
    	# [{'flag':'<flag>','msg':'<server response msg>'},{...},...]
        return self.submit_fn(flags)
    
  
    
    
    
def loop(app: Flask):
    with app.app_context():
        logger = current_app.logger  # Need to get it before sleep, otherwise it doesn't work. Don't know why.
        # Let's not make it start right away
        time.sleep(5)
        logger.info('starting.')
        database = db.get_db()
        queue = OrderedSetQueue()
        
        submitter = Submitter(current_app.config, current_app.config['SUB_TYPE'])
        
        logger.info('submitter-class ok')
        
        while True:
            
            s_time = time.time()
            expiration_time = (datetime.now() - timedelta(seconds=current_app.config['FLAG_ALIVE'])).replace(microsecond=0).isoformat(sep=' ')
            cursor = database.cursor()
            cursor.execute('''
            SELECT flag
            FROM flags
            WHERE time > ? AND status = ? AND server_response IS NULL
            ORDER BY time DESC 
            ''', (expiration_time, current_app.config['DB_NSUB']))
            for flag in cursor.fetchall():
                queue.put(flag[0])
            i = 0
            queue_length = queue.qsize()
            try:
                # Send N requests per interval
                while i < min(current_app.config['SUB_LIMIT'], queue_length):
                    # Send N flags per request
                    flags = []
                    for _ in range(min(current_app.config['SUB_PAYLOAD_SIZE'], queue_length)):
                        flags.append(queue.get())
                    print(flags)
                    
                    if 'custom' in current_app.config['SUB_TYPE']:
                        submit_result = submitter.submit(flags, sub_fun=current_app.config['CUSTOM_SUBMITTER_FUNCTION']  ,keywords=current_app.config['CUSTOM_KEYWORDS'])
                    else:
                        submit_result = submitter.submit(flags)
                    # executemany() would be better, but it's fine like this.
                    for item in submit_result:
                        if (submitter.SUB_INVALID.lower() in item['msg'].lower() or
                                submitter.SUB_YOUR_OWN.lower() in item['msg'].lower() or
                                submitter.SUB_STOLEN.lower() in item['msg'].lower() or
                                submitter.SUB_NOP.lower() in item['msg'].lower()):
                            cursor.execute('''
                            UPDATE flags
                            SET status = ?, server_response = ?
                            WHERE flag = ?
                            ''', (current_app.config['DB_SUB'], current_app.config['DB_ERR'], item['flag']))
                        elif submitter.SUB_OLD.lower() in item['msg'].lower():
                            cursor.execute('''
                            UPDATE flags
                            SET status = ?, server_response = ?
                            WHERE flag = ?
                            ''', (current_app.config['DB_SUB'], current_app.config['DB_EXP'], item['flag']))
                        elif submitter.SUB_ACCEPTED.lower() in item['msg'].lower():
                            cursor.execute('''
                            UPDATE flags
                            SET status = ?, server_response = ?
                            WHERE flag = ?
                            ''', (current_app.config['DB_SUB'], current_app.config['DB_SUCC'], item['flag']))
                        i += 1
            except requests.exceptions.RequestException:
                logger.error('Could not send the flags to the server, retrying...')
            finally:
                # At the end, update status as EXPIRED for flags not sent because too old
                cursor.execute('''
                                    UPDATE flags
                                    SET server_response = ?
                                    WHERE status LIKE 'NOT_SUBMITTED' AND time <= ?
                                    ''', (current_app.config['DB_EXP'], expiration_time))
                database.commit()
                duration = time.time() - s_time
                if duration < current_app.config['SUB_INTERVAL']:
                    time.sleep(current_app.config['SUB_INTERVAL'] - duration)
