# This script works with Ubuntu 20.04 and above.
# Older version of Ubuntu do not have /etc/netplan.

import paramiko
import getpass
import time

ip_address = '192.168.1.84'
username = input('Enter SSH username: ')
password = getpass.getpass(prompt='Enter SSH password: ')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(ip_address, username=username, password=password)
    print('Successfully connected to', ip_address)
    
    # execute command and retrieve output
    stdin, stdout, stderr = ssh.exec_command('ls /etc/netplan')
    output = stdout.readlines()
    
    # print output
    filename = output[0].strip()
    print("the name of the network configuration file is: " , filename)
    print("Creating a backup file ...")
    backup_filename = filename + ".bkp"
    print("The name of the backup file is: ", backup_filename)
    
    # Full path of the netplan config file.
    config_file = "/etc/netplan/" + filename
    print("------> Full Path:",config_file)
    
    backup_command = f'sudo cp /etc/netplan/{filename} /etc/netplan/{backup_filename}'
    stdin, stdout, stderr = ssh.exec_command(backup_command)
    stdin.close()

    print(f'Backup created Successfully.')
    
    
    # Prompt for interface name and IP configuration
    interface_name = input('Enter interface name: ')
    ip_address = input('Enter IP address: ')
    netmask = input('Enter subnet mask in CIDR notation without backslash: ')
    gateway = input('Enter default gateway IP address: ')
    dns_servers = input('Enter comma-separated DNS server IP addresses: ')
    


    # Generate new netplan configuration
    config_template = f"""
    network:
        version: 2
        renderer: networkd
        ethernets:
            {interface_name}:
                dhcp4: no
                addresses: [{ip_address}/{netmask}]
                gateway4: {gateway}
                nameservers:
                    addresses: [{dns_servers}]
    """
    
    # Write new netplan configuration to file
    with ssh.open_sftp() as sftp:
        with sftp.file(config_file, 'w') as file:
            file.write(config_template)


    # Apply new network configuration
    stdin, stdout, stderr = ssh.exec_command('sudo netplan apply')
    stdin.close()
    
    
        
except paramiko.AuthenticationException:
    print('Authentication failed. Please check your credentials.')
except Exception as e:
    print('An error occurred:', e)
finally:
    ssh.close()
