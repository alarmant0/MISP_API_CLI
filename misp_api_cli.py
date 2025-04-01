import requests as r
import json
import warnings
from datetime import datetime
import pyfiglet
import os
import signal
import sys
import time
import shutil

'''
TODO LIST:
- Adicionar user **Done**
- Remover users **Done**
- Password reset aos users **Semi TODO**
- Add feeds **Semi Done**
- Get a list of feeds **Done**
- Get a feed by ID **Done**
- Enable and disable feed **Done**
- Fetch all feeds **Done**
- Requirements.txt **Done**
- Add default cronjobs TODO
- Add custom cronjobs TODO
- List cronjobs **Done**
- Add event TODO
- List events TODO
- List event by ID TODO
- List events filtered TODO
- Search events TODO
- Publish an event TODO
- Delete an event TODO
'''

warnings.filterwarnings("ignore")

token = "TOKEN"

headers = {
	'Authorization': token,
	'Accept': 'application/json',
	'Content-Type': 'application/json'
}

DOMAIN="https://misp.local"

def isInvalidID(response):
	if response.json().get("message") == "Invalid user" or response.json().get("name") == "Invalid user":
		return True
	return False

def signal_handler(sig, frame):
	os.system('clear')
	print_banner()
	print("Ctrl+C detected\nBye bye.")
	time.sleep(1)
	os.system('clear')
	sys.exit(0)

def print_help_menu():
	os.system('clear')
	ascii_help = pyfiglet.figlet_format(" 									     Help")
	print(ascii_help.center(shutil.get_terminal_size().columns))
	help_string = """
	 This script uses MISP API to navigate throughout MISP functionalities, using CLI instead of a GUI.
	"""
	print(help_string)

def print_banner():
	ascii_misp = pyfiglet.figlet_format("MISP - Paldata")
	print(f"\033[31m{ascii_misp}\033[0m")

def print_users():
	URL = "https://misp.local/admin/users"

	response = r.get(url=URL, headers=headers, verify=False)
	response_json = response.json()

	# print("Response: ", response.text)
	if response.status_code == 200:
		print("\n\033[32mHTTP Code:", response.status_code, "\n")
	else:
		print("\n\033[31mHTTP Code:", response.status_code, "\n")
	for i in range(len(response_json)):
		json = response_json[i].get("User")
		# print(response_json[i])
		id=json.get("id")
		email=json.get("email")
		last_login_unix = int(json.get("last_login"))
		date_modified_unix = int(json.get("date_modified"))
		last_api_access_unix = int(json.get("last_api_access"))
		current_login_unix = int(json.get("current_login"))
		last_pw_change_unix = int(json.get("last_pw_change"))
		date_modified = datetime.utcfromtimestamp(date_modified_unix)
		last_api_access = datetime.utcfromtimestamp(last_api_access_unix)
		current_login = datetime.utcfromtimestamp(current_login_unix)
		last_pw_change = datetime.utcfromtimestamp(last_pw_change_unix)
		last_login = datetime.utcfromtimestamp(last_login_unix)
		print("\033[1;31mID:\033[0m", id, "\nUser:", email,  "\nLast Login:", last_login, "\nDate Modified:", date_modified, "\nLast API Access:", last_api_access, "\nCurrent Login:", current_login, "\nLast Password Change:", last_pw_change, "\n")

def add_user(email="testeapi@api.com", org_id="1", change_pw="0"):
	URL = "https://misp.local/admin/users/add"
	data = {
		'org_id' : org_id,
		'email' : email,
		'change_pw' : change_pw
	}
	response = r.post(url=URL,headers=headers, json=data, verify=False)
	if response.json().get("errors"):
		error = response.json().get("errors").get("email")[0]
		print(f'\n\033[1;31m{error}\033[0m\n')
		return
	# print(response.json().get("User"))
	email = response.json().get("User").get("email")
	password = response.json().get("User").get("password")
	print(f'\n\033[1;32mSucesso\033[0m', '\n\nEmail:', email, '\nPassword:', password, '\n')

def print_user_by_id(userID):
	URL = f"https://misp.local/admin/users/view/{userID}"
	data = {
		'userId' : userID
	}
	response = r.get(url=URL, headers=headers, verify=False)
	# print(response.text)
	if response.json().get("name") == "Invalid user" or response.json().get("message") == "Invalid user":
		print("\n\033[1;31mInvalid User ID\033[0m\n")
		return
	json = response.json().get("User")
	id=json.get("id")
	email=json.get("email")
	last_login=datetime.utcfromtimestamp(int(json.get("last_login")))
	date_modified=datetime.utcfromtimestamp(int(json.get("date_modified")))
	last_api_access = datetime.utcfromtimestamp(int(json.get("last_api_access")))
	current_login = datetime.utcfromtimestamp(int(json.get("current_login")))
	print("\n")
	print("\033[1;31mID:\033[0m", id, "\nUser:", email, "\nLast Login:", last_login, "\nDate Modified:", date_modified, "\nCurrent Login:", current_login, "\nLast API Access:", last_api_access, "\n")

def delete_user_by_id(userID):
	URL = f'https://misp.local/admin/users/delete/{userID}'
	data = {
		'userId' : userID
	}
	response = r.post(url=URL, headers=headers, verify=False)
	if isInvalidID(response):
		print("\n\033[1;31mInvalid user ID\033[0m\n")
	else:
		message = response.json().get("message")
		print("\n\033[1;31mMessage:", message, "\n\033[0m")

def print_crontabs_menu():
	print("\nAdd default cronjobs - 1\nAdd custom cronjobs - 2\nList cronjobs - 3\n")
	user_input = str(input("> ")).lower()
	match user_input:
		case "1":
			add_cronjob()
		case "2":
			return
		case "3":
			list_cronjobs()

def add_cronjob():
	print("\nFetch new feeds daily - 1\n")
	user_input = str(input("> "))
	crontab = ""
	match user_input:
		case "1":
			crontab = f'0 1 * * * root /usr/bin/curl -X POST --insecure --header "Authorization: {token}" --header "Accept: application/json" --header "Content-Type: application/json" https://misp.local/feeds/fetchFromAllFeeds'
		case default:
			print("\nInvalid choice\n")
			return
	if len(crontab) != 0:
		if os.path.exists("/etc/crontab"):
			try:
				with open("/etc/crontab" , 'a') as f:
					f.write(crontab)
				f.close()
			except Exception as e:
				print(f'\033[1;32mCan not open the file, run as sudo\033[0m')
			# os.system(f'echo {crontab} >> /etc/crontab')

def list_cronjobs():
	file_path = '/etc/crontab'
	if os.path.exists(file_path):
		try:
			with open(file_path, 'r') as f:
				for l in f:
					first_char = l[0]
					if first_char.isdigit():
						print(f'\033[1;30m{l}\033[0m')
		except Exception as e:
			print(f'Error reading file: {e}')
	else:
		print("\n\033[1;31mYou have no /etc/crontab file on your system... Weird...\033[0m\n")

def print_events(limit=10):
	URL=f'https://misp.local/events'
	response = r.get(url=URL, headers=headers, verify=False)
	json=response.json()
	limit = int(limit)
	for i in range(0, limit):
		event=json[i]
		id=event.get("id")
		info=event.get("info")
		date=event.get("date")
		print(f'\nID: {id}\nInfo: {info}\nDate: {date}\n')

def print_event_by_id(id):
	URL=f'https://misp.local/events/view/{id}'
	print("Teste")

def print_events_menu():
	print(f'\nList events - 1\nSearch events - 2\nGet event by ID - 3\nFiltered search - 4\nAdd event - 5\nDelete event - 6\n')
	user_input = str(input("> ")).lower()
	match user_input:
		case "1":
			limit = str(input("Limit (Default 10) > "))
			print_events(limit)
		case "2":
			id = str(input("ID > "))
			print_event_by_id(id)
		case "3":
			return
		case "4":
			return
		case "5":
			return
		case "6":
			return
		case default:
			print("\nInvalid choice\n")

def print_menu():
	print("Users - 1\nFeeds - 2\nEvents - 3\nOrganisations - 4\nTags - 5\nCronjobs - 6\n\nCtrl+C to exit the program :)\n")
	user_input = str(input("> "))
	user_input = user_input.lower()
	match user_input:
		case "1":
			print_users_menu()
		case "2":
			print_feeds_menu()
		case "3":
			print_events_menu()
		case "4":
			return
		case "5":
			return
		case "6":
			print_crontabs_menu()
		case "clear":
			clear_screen_and_print()
		case "c":
			clear_screen_and_print()
		case default:
			print("\033[1;31mEscolha inválida\033[0m\n")

def reset_password_by_id(userID, firstTime=0):
	URL=f'https://misp.local/users/initiatePasswordReset/{userID}/{firstTime}'
	response = r.post(url=URL, headers=headers, verify=False)
	if isInvalidID(response):
		print("\n\033[1;31mInvalid user ID\n\033[0m")
	elif response.json().get("errors"):
		message =  response.json().get("errors")
		print(f'\n\033[1;31m{message}\033[0m\n')
	else:
		# print(response.json())
		message = response.json().get("success")
		print(f'\n\033[1;32m{message}\n\033[0m')

def add_feed(name, provider, url, rules, enabled, distribution, sharing_group_id, tag_id, source_format):
	URL=f'https://misp.local/feeds/add'
	data = {
		'name' : name,
		'provider' : provider,
		'url' : url,
		'rules' : rules,
		'enabled' : enabled,
		'distribution' : distribution,
		'sharing_group_id' : sharing_group_id,
		'tag_id' : tag_id,
		'source_format' : source_format
	}
	response = r.post(url=URL, headers=headers, json=data, verify=False)
	print(f'\n{response.json().get("message")}\n')

def print_feeds_menu():
	clear_screen_and_print()
	print("List feeds - 1\nGet feed by ID - 2\nAdd feed - 3\nEnable/Disable feed - 4\nFetch all Feeds - 5\n\nBack/b to go back to the main menu\n")
	user_input = str(input("> ")).lower()
	match user_input:
		case "1":
			user_input = str(input("\nLimit (Default 10) > "))
			if not user_input:
				user_input = 10
			print_feeds(user_input)
		case "2":
			user_input = str(input("\nFeed's ID > "))
			print_feed_by_id(user_input, headers)
		case "3":
			name = str(input("\nName > "))
			provider = str(input("Provider > "))
			url=str(input("URL > "))
			rules=str(input("Rules > "))
			enabled=str(input("Enabled (True or False) > ")).lower()
			if enabled != "false" and enabled != "false":
				enabled="false"
			distribution=str(input("Distribution (0,1,2,3,4,5) > "))
			if not distribution in range(0,5):
					distribution="0"
			source_format=str(input("Source Format (csv, freetext, misp) > "))
			publish=str(input("Publish > "))
			input_source=str(input("Input Source (local or network) > "))
			add_feed(name, provider, url, rules, enabled, distribution, source_format, publish, input_source)
		case "5":
			fetchAllFeeds()
		case "4":
			id = str(input("Feed's ID > "))
			action = str(input("Enable or disable feed > ")).lower()
			enable_disable_feed(id,action)
		case "b":
			clear_screen_and_print()
			return
		case "back":
			clear_screen_and_print()
			return
		case default:
			print("Invalid choice")

def enable_disable_feed(id, action="enable"):
	URL=f'https://misp.local/feeds/'
	match action:
		case "disable":
			URL +=f"disable/{id}"
		case "enable":
			URL +=f"enable/{id}"
		case default:
			print(f'\n\033[1;30mInvalid choice\033[0m\n')
	response = r.post(url=URL, headers=headers, verify=False)
	message = response.json().get("message")
	print(f'\n\033[1;32m{message}\033[0m\n')

def fetchAllFeeds():
	URL=f'https://misp.local/feeds/fetchFromAllFeeds'
	response = r.post(url=URL, headers=headers, verify=False)
	message = response.json().get("result")
	print(f'\n\033[1;32m{message}\033[0m\n')

def print_feed_by_id(feedId, headers):
	URL=f"https://misp.local/feeds/view/{feedId}"
	# print(headers)
	response = r.get(url=URL, headers=headers, verify=False)
	json = response.json().get("Feed")
	id=json.get("id")
	provider=json.get("provider")
	name=json.get("name")
	url=json.get("url")
	rules=json.get("rules")
	enabled=json.get("enabled")
	distribution=json.get("distribution")
	source_format=json.get("source_format")
	headers=json.get("headers")
	orgc_id=json.get("orgc_id")
	coverage=json.get("coverage_by_other_feeds")
	print(f'\nID: {id}\nProvider: {provider}\nName: {name}\nURL: {url}\nRules: {rules}\nEnabled: {enabled}\nDistribution: {distribution}\nSource: {source_format}\nHeaders: {headers}\nOrgc_ID: {orgc_id}\nCoverage: {coverage}\n')

def print_feeds(limit=5):
	URL=f'https://misp.local/feeds'
	limit = int(limit)
	# print(headers)
	response = r.get(url=URL, headers=headers, verify=False)
	# print(response.json()[0].get("Feed"))
	for i in range(0,limit):
		feed = response.json()[i].get("Feed")
		id=feed.get("id")
		provider = feed.get("provider")
		url=feed.get("url")
		enabled = feed.get("enabled")
		name=feed.get("name")
		print(f'\nID: {id}\nName: {name}\nProvider: {provider}\nURL: {url}\nEnabled: {enabled}\n')
	# print(response.text[0:100])

def print_users_menu():
	clear_screen_and_print()
	print("List Users - 1\nGet User by ID - 2\nAdd User - 3\nDelete User - 4\nReset User password - 5\n\nBack/b to go back to the main menu\n")
	user_input = str(input("> "))
	match user_input:
		case "1":
			print_users()
		case "2":
			userID = str(input("\nID > "))
			print_user_by_id(userID)
		case "3":
			email = str(input("Email > "))
			add_user(email)
		case "4":
			userID = str(input("ID > "))
			delete_user_by_id(userID)
		case "5":
			userID = str(input("ID > "))
			reset_password_by_id(userID)
		case "b":
			clear_screen_and_print()
			return
		case "back":
			clear_screen_and_print()
			return
		case default:
			print("Invalid choice")

def print_line_break():
	print("-----------------------------------------------\n")

def clear_screen_and_print():
	os.system('clear')
	print_banner()

def main():
	clear_screen_and_print()
	while True:
		print_menu()

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	n = len(sys.argv)
	if n != 1:
		for i in range(1,n):
			if sys.argv[i] == "-h":
				print_help_menu()
	else:
		main()
