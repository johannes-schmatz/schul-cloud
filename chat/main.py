#!/usr/bin/python3
#    <desc>
#    Copyright (C) 2020  Johannes Schmatz <johannes_schmatz@gmx.de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import requests
import sys

import logindata
# has to contain:
## url="https://chat.schul-cloud.org"
## token="ArvuVv..."
## userid="smJ..."
## names=["8c-Team.49kl","MU-8c.e3r4"]

url = logindata.url + "/api/v1/login"
payload = {"resume": logindata.token}
r = requests.post(url, data=payload)
if r.json()['status'] == 'success':
	sys.stderr.write("login suceess\n")

def get_last_messages_for_group(groupname, number=3, def_pad_len=20, \
	pad_ts=" -> ", pad_usr=" - "):
	url = logindata.url + "/api/v1/groups.history"
	headers = {'X-Auth-Token': logindata.token, 'X-User-Id': \
		logindata.userid}
	payload = {'roomName': groupname}
	r = requests.get(url, params=payload, headers=headers)
	r = r.json()['messages']
	for i in range(0, number):
		if r[i]['u']['name'] == "Schulcloud":
			number += 1
	for i in range(0, number):
		d = r[i]
		if d['u']['name'] == "Schulcloud":
			continue
		if len(groupname) > def_pad_len:
			groupname = groupname[:def_pad_len -1]
			pad = " "
		else:
			pad = " " * (def_pad_len - len(groupname))
		msg_arr = []
		j = 0
		this_msg = ""
		while j != len(d['msg']):
			if d['msg'][j] == "\n":
				this_msg = this_msg + " "
			else:
				this_msg = this_msg + d['msg'][j]
			if (j % 30 == 0 and j > 30 - 1) or \
				j == len(d['msg']) -1:
				msg_arr.append(this_msg)
				this_msg = ""
			j += 1
#		if i != 0:
#			print("")
		for j in msg_arr:
			if j == msg_arr[0]:
				print(groupname + pad + " " + \
				str(i) + " " + d['ts'] + pad_ts + j + \
				pad_usr + d['u']['name'])
			else:
				print(" " * (def_pad_len + 3 + \
				len(d['ts']) + len(pad_ts)) + j)
	return r

def get_messages():
	for i in logindata.names:
		get_last_messages_for_group(i)

def send_message_to_id(groupid, message):
	url = logindata.url + "/api/v1/chat.sendMessage"
	headers = {'X-Auth-Token': logindata.token, 'X-User-Id': \
		logindata.userid}
	payload = {'message': {'rid': groupid, \
		'msg': message}}
	r = requests.post(url, json=payload, headers=headers)
	return r

def get_group_id_for_name(name):
	url = logindata.url + "/api/v1/groups.info"
	headers = {'X-Auth-Token': logindata.token, 'X-User-Id': \
		logindata.userid}
	payload = {'roomName': name}
	r = requests.get(url, params=payload, headers=headers)
	return r.json()['group']['_id']


def send_group(groupname, msg):
	send_message_to_id(get_group_id_for_name(groupname), msg)

def search_name_in_im(name_of_ohter):
	url = logindata.url + "/api/v1/im.list"
	headers = {'X-Auth-Token': logindata.token, 'X-User-Id': \
		logindata.userid}
	r = requests.get(url, headers=headers)
	names = []
	ids = []
	for i in r.json()['ims']:
		for j in i['usernames']:
			if not j in names:
				names.append(j)
				ids.append(i['_id'])
	for i in range(0, len(names)):
		if re.search(name_of_ohter, names[i]):
			return (names[i], ids[i])

def send_direct(name_of_other, msg):
	name, id_of_other = search_name_in_im(name_of_other)
	return send_message_to_id(id_of_other, msg)

def help_func():
	print("""
HELP for main.py for schul-cloud-chat
./main.py [--help|-h] ............................... call the help
......... (-g|--group-id) "name" .................... get the group id for name
......... (-i|--id) "id" "message" .................. send message to id
......... (-l|--logindata) .......................... dump all logindata
......... (-m|--match) "name" "message" ............. send message to fist match of -s of name
......... (-n|--group-match) "group" "message" ...... send message to the answer of -g of group
......... (-p|--print-groups) ....................... print groups of logindata.names
......... (-r|--read) ............................... read the messages
......... (-s|--search) "pattern" ................... search id of direct messages user""")

if __name__ == "__main__":
	try:
		if len(sys.argv) == 2:
			if sys.argv[1] == "-r" or sys.argv[1] == "--read":
				get_messages()
			elif sys.argv[1] == "-p" or sys.argv[1] == "--print-groups":
				print(logindata.names)
			elif sys.argv[1] == "-l" or sys.argv[1] == "--logindata":
				print('url = "' + logindata.url + '"')
				print('token = "' + logindata.token + '"')
				print('userid = "' + logindata.userid + '"')
				print('names = ' + str(logindata.names))
			else:
				help_func()
		elif len(sys.argv) == 3:
			if sys.argv[1] == "-s" or sys.argv[1] == "--search":
				name, id_of = search_name_in_im(sys.argv[2])
				print(name + ":" + id_of)
			elif sys.argv[1] == "-g" or sys.argv[1] == "--group-id":
				print(get_group_id_for_name(sys.argv[2]))
		elif len(sys.argv) == 4:
			im_id = sys.argv[2]
			im_msg = sys.argv[3]
			if sys.argv[1] == "-i" or sys.argv[1] == "--id":
				send_message_to_id(im_id, im_msg)
			elif sys.argv[1] == "-m" or sys.argv[1] == "--match":
				send_direct(im_id, im_msg)
			elif sys.argv[1] == "-n" or sys.argv[1] == "--group-match":
				gid = get_group_id_for_name(im_id)
				send_message_to_id(gid, im_msg)
	except:
		sys.stderr.write("Something went wrong!!!\n")

# syntax
# vim: ts=8 sts=8 sw=8 noet si
