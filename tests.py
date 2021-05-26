from flask import Flask, json
import unittest

import requests
from requests import status_codes
import responses
from unittest.mock import patch
from random import randint
from datetime import datetime


class TestCase(unittest.TestCase):
    
    token = ''
    num = randint(1,999)
    user_id = 0
    task_id = 0

    @responses.activate  
    def testGetUser(self):
        responses.add(**{
        'method'         : responses.GET,
        'url'            : 'http://127.0.0.1:5000/api/users/1',
        'body'           : '',
        'status'         : 200,
        'content_type'   : 'application/json'
        })

        response = requests.get('http://127.0.0.1:5000/api/users/1')
        self.assertEqual(200, response.status_code)

    @responses.activate  
    def testGetTask(self):
        responses.add(**{
            'method'         : responses.GET,
            'url'            : 'http://127.0.0.1:5000/api/tasks/1',
            'body'           : '',
            'status'         : 200,
            'content_type'   : 'application/json'
        })

        response = requests.get('http://127.0.0.1:5000/api/tasks/1')
        self.assertEqual(200, response.status_code)

   
#User Methods
    @patch('requests.post')
    def test1_post_user(self, mock_post):
        url = "http://127.0.0.1:5000/api/users"
        
        payload1={'user': '{"email":"cruz' + str(self.__class__.num) + '@sting.com", "password":"test1","full_name":"Cruz Valerio","photo":""}'}
        headers = {}
    
        result_post = requests.request("POST", url, headers=headers, data=payload1)
        print(result_post.json())
        self.__class__.user_id = result_post.json()['id']
        self.assertEqual(result_post.status_code, 200)
    
    
    @patch('requests.post')
    def test2_login_method(self, mock_post):
       
        info = {"user": '{"email" : "cruz' + str(self.__class__.num) + '@sting.com", "password": "test1"}'}
        result_login = requests.request("POST", "http://127.0.0.1:5000/api/login", headers={}, data=info)
        print(result_login.json())
        print(info)
        token = result_login.json()['token']
        self.__class__.token = token

        resp = requests.post("http://127.0.0.1:5000/api/login", data=json.dumps(info), headers={'Content-Type': 'application/json'})
        mock_post.assert_called_with("http://127.0.0.1:5000/api/login", data=json.dumps(info), headers={'Content-Type': 'application/json'})    

    
    def test3_put_user(self):
        url = "http://127.0.0.1:5000/api/users"

        response_user = requests.get('http://127.0.0.1:5000/api/users/' + str(self.__class__.user_id))
        user_modified = response_user.json()
       
        user_modified['full_name'] = 'Test Name'       
        payload={"user": json.dumps(user_modified),"token": self.__class__.token}
        headers = {}
        print(payload)
        result_put = requests.request("PUT", url, headers=headers, data=payload)
        self.assertEqual(result_put.status_code, 200)
        self.assertIn(result_put.text, 'User Updated')

   #Tasks Methods
    
    @patch('requests.post')
    def test4_post_task(self, mock_post):
        url = "http://127.0.0.1:5000/api/tasks"
        
        payload1={'user_id': str(self.__class__.user_id),
                'task': '{"title":"title task ' + str(self.__class__.num) + ' ","description":"description task","start_date":"2021-05-26", "due_date":"2021-05-30", "id":1}',
                'token': self.__class__.token}
        headers = {}
    
        result_post = requests.request("POST", url, headers=headers, data=payload1)
        print('POST TASK')
        print(result_post.json())
        self.__class__.task_id = result_post.json()['task_id']
        self.assertEqual(result_post.status_code, 200)
    
    def test5_put_task(self):
        url = "http://127.0.0.1:5000/api/tasks"

        response_task = requests.get('http://127.0.0.1:5000/api/tasks/' + str(self.__class__.task_id))
        task_modified = response_task.json()
       
        task_modified['description'] = 'Test description updated' 
  
        payload={"task": json.dumps(task_modified),"token": self.__class__.token}
        headers = {}
        print('UPDATE TASK')
        print(payload)
        result_put = requests.request("PUT", url, headers=headers, data=payload)
        print(result_put.text)
        self.assertEqual(result_put.status_code, 200)
        self.assertIn(result_put.text, 'Task Updated')

    def test6_delete_task(self):
        url = "http://127.0.0.1:5000/api/tasks"

        payload1={'id': self.__class__.task_id, 'token': self.__class__.token}
        print(payload1)
        headers = {}
       
        result_delete = requests.request("DELETE", url, headers=headers, data=payload1)
       
        self.assertEqual(result_delete.status_code, 200)
        self.assertIn(result_delete.text, 'Task Deleted') 

    
    def test7_delete_user(self):
        url = "http://127.0.0.1:5000/api/users"

        payload1={'id': self.__class__.user_id, 'token': self.__class__.token}
        print(payload1)
        headers = {}
       
        result_delete = requests.request("DELETE", url, headers=headers, data=payload1)
       
        self.assertEqual(result_delete.status_code, 200)
        self.assertIn(result_delete.text, 'User Deleted') 
    

    
    
if __name__ == '__main__':
    unittest.main() 