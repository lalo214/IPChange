import socket
import paramiko
from getpass import getpass
import time


# ssh into management IP to change it's ip
def change_ip():
    # open file of IP's to SSH into
    with open('oldIPs.txt') as f:
        ip_list = [x.strip('\n') for x in f]

    mask = input('Enter subnet mask (x.x.x.x): ')
    new_ip = input('Enter first new IP to be created: ')

    # need loop for exception handling
    login_invalid = True
    while login_invalid:
        username = input('Enter username: ')
        password = getpass()

        # new_ip is split to separate subnet from unique address
        new_ip_list = new_ip.split('.')
        subnet = '.'.join(new_ip_list[0:3])
        incremented_ip = int(new_ip_list[3])

        # iterate through list of IPs to SSH to each one
        for i in range(len(ip_list)):
            ip = (ip_list[i].strip('\n'))
            # attempt to connect to SSHClient
            try:
                remote_conn_pre = paramiko.SSHClient()
                remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                remote_conn_pre.connect(ip, timeout=3, port=22, username=username, password=password,
                                        look_for_keys=False, allow_agent=False)
            except paramiko.AuthenticationException:
                print("Authentication failed. Please verify credentials: ")
                break

            except paramiko.SSHException:
                print("Unable to establish SSH connection to:", ip)
                continue
            # exception required for timeout errors
            except socket.error:
                print("Unable to establish SSH connection to:", ip)
                continue

            login_invalid = False
            remote_conn = remote_conn_pre.invoke_shell()
            # commands sent to CLI
            remote_conn.send("en\n")
            remote_conn.send("conf t\n")
            remote_conn.send("int vlan 1\n")
            remote_conn.send('ip add' + ' ' + subnet + '.' + str(incremented_ip) + ' ' + mask + '\n')

            incremented_ip += 1
            time.sleep(.5)
            output = remote_conn.recv(65535).decode('utf-8')
            # print(ip, 'changed to', subnet + '.' + str(incremented_ip), file=open('newIPs.txt', 'a'))
            # need to print new and old IP to verify change


# SSH into new management IP to change default gateway
def change_gateway(gateway):
    # open file of IP's to SSH into
    with open('newIPs.txt') as f:
        ip_list = [x.strip('\n') for x in f]

    # need loop for exception handling
    login_invalid = True
    while login_invalid:
        username = input('Enter username: ')
        password = getpass()

        # iterate through list of IPs to SSH to each one
        for i in range(len(ip_list)):
            ip = (ip_list[i].strip('\n'))
            # attempt to connect to SSHClient
            try:
                remote_conn_pre = paramiko.SSHClient()
                remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                remote_conn_pre.connect(ip, timeout=3, port=22, username=username, password=password,
                                        look_for_keys=False, allow_agent=False)
            except paramiko.AuthenticationException:
                print("Authentication failed. Please verify credentials: ")
                break

            except paramiko.SSHException:
                print("Unable to establish SSH connection to:", ip)
                continue
            # exception required for timeout errors
            except socket.error:
                print("Unable to establish SSH connection to:", ip)
                continue

            login_invalid = False
            remote_conn = remote_conn_pre.invoke_shell()
            # commands sent to CLI
            remote_conn.send("en\n")
            remote_conn.send("conf t\n")
            remote_conn.send('ip default-gateway' + ' ' + gateway + '\n')
            remote_conn.send("exit\n")
            remote_conn.send("wr mem\n")

            time.sleep(.5)
            output = remote_conn.recv(65535).decode('utf-8')
            # print output to verify


change_ip()
new_gateway = input('Enter the gateway:')
change_gateway(new_gateway)
