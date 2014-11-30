from flask import Flask
from flask import request
from flask import render_template
import string
import random
import twilio.twiml
import os
from pexpect import pxssh
import requests
from twilio.rest import TwilioRestClient

app = Flask(__name__)
sa = pxssh.pxssh()

#Twilio
account_sid = ""
auth_token = ""
client = TwilioRestClient(account_sid, auth_token)

#YO
api_token = ""


#Credentials
ssh_host = ""
ssh_user = ""
ssh_pass = ""

vpn_host = ""
vpn_user = ""
vpn_pass = ""
show_command1 = ""
show_command2 = ""
show_command3 = ""



@app.route('/')
def my_form():
	return render_template("template.html")

@app.route('/', methods=['POST'])
def my_form_post():

	#User and password
	username = str("u" + ''.join(random.choice(string.digits) for i in range(6)))
	password = str(''.join(random.choice(string.ascii_lowercase) for i in range(7)))

	#vars from the form
	f_option = request.form['f_option']
	open_port = request.form['open_port']
	phone_number = request.form['phone_number']
	r_host  = request.form['r_host']
	r_port  = request.form['r_port']
	yo_user = request.form['yo_username']
	
	#YO
	requests.post("http://api.justyo.co/yo/", data={'api_token': api_token, 'username': yo_user})

	if f_option == 'ssh_proxy' or f_option == 'ssh_ports':
		
		command1 = str('useradd ' + username)
		command2 = str('echo -e "' + password + r'\n' + password + r'\n" | passwd ' + username)
		command3 = str('iptables -t nat -A PREROUTING -p tcp --dport ' + open_port + ' -j REDIRECT --to-port 22')
		command4 = str('iptables -t nat -A PREROUTING -p udp --dport ' + open_port + ' -j REDIRECT --to-port 22')
		command9 = str('echo ' + f_option + '> aaaa.txt')
		sa.login(ssh_host, ssh_user, ssh_pass)
		sa.sendline(command1)
		sa.sendline(command2)
		sa.sendline(command3)
		sa.sendline(command4)
		sa.sendline(command9)
		sa.prompt()
		sa.logout()
		
		if f_option == 'ssh_proxy':
			body_message = "Hi \nIP Address: IP\nUser: " + username + " \nPass: " + password + "\nOpen your terminal and run: ssh -D 20080 -f -C -q -N " + username + "@IP -p " + open_port + "\nThen: Sys Preferences > Network > Advanced > Proxies > Add Socks Proxy -> localhost:20080\nThat's it!"
			show_command1 = "ssh -D 20080 -f -C -q -N " + username + "@IP -p " + open_port
			comment1 = "Run the command. Go to System Preferences > Network > Advanced > Proxies > Add SOCKS Proxy using localhost:20080"
		elif f_option == 'ssh_ports':
			body_message = "Hi \nIP Address: IP\nUser: " + username + " \nPass: " + password + "\nOpen your terminal and run: ssh -f " + username + "@IP -L 10080:" + r_host + ":" + r_port + " -N -p " + open_port + "\nNow use localhost:10080 to connect to the server"
			show_command1 = "ssh -f " + username + "@IP -L 10080:" + r_host + ":" + r_port + " -N -p " + open_port
			comment1 = "Run the command in your terminal. After that use localhost:10080 to connect to the server."
		else:
			pass
		

	elif f_option == 'vpn':
		body_message = "Hi \nIP Address: IP\nUser: " + username + " \nPass: " + password + "\nPort: " + open_port + "\nUse these details to configure your VPN client"
		
		command1 = str('useradd ' + username)
		command2 = str('echo -e "' + password + r'\n' + password + r'\n" | passwd ' + username)
		command3 = str('iptables -t nat -A PREROUTING -p tcp --dport ' + open_port + ' -j REDIRECT --to-port 443')
		command4 = str('iptables -t nat -A PREROUTING -p udp --dport ' + open_port + ' -j REDIRECT --to-port 443')
		command9 = str('echo ' + f_option + '> aaaa.txt')
		sa.login(vpn_host, vpn_user, vpn_pass)
		sa.sendline(command1)
		sa.sendline(command2)
		sa.sendline(command3)
		sa.sendline(command4)
		sa.sendline(command9)
		sa.prompt()
		sa.logout()
		
		comment1 = "Use these details to configure your VPN Client"
		show_command1 = ""
	else:
		return render_template("error.html")

	message = client.messages.create(to=phone_number, from_="+441133203095", body=body_message)
	return render_template(str(f_option) + ".html", f_option=f_option, username=username, password=password, ssh_host=ssh_host, vpn_host=vpn_host, show_command1=show_command1, comment1=comment1, open_port=open_port)

if __name__ == '__main__':
	app.run(debug=True)
