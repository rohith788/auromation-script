import logging
import urllib.request
import sys
import time

import boto3
import yaml

from key_pair import KeyPairWrapper
from instance import InstanceWrapper
from security_group import SecurityGroupWrapper

class Solution: 
    def __init__(self, sg_group_name, server_config, disk_config, user_config):
        self.key_pair_obj = KeyPairWrapper.from_resource()
        self.inst_wrapper = InstanceWrapper.from_resource()
        self.sg_wrapper = SecurityGroupWrapper.from_resource()
        self.sg_group_name = sg_group_name
        self.server_config = server_config 
        self.disk_config = disk_config
        self.user_config = user_config

    #create the key pair for ssh
    def create_key_pair(self, key_name):
        response = self.key_pair_obj.create(key_name) #create the key
        print('key pair created')
        self.key_pair_obj.list(5)
        ec2_client = boto3.client('ec2', region_name="us-east-2")
        key = ec2_client.describe_key_pairs(
            KeyNames=[key_name],
            IncludePublicKey=True
            )
        public_key = "" 
        print(key['KeyPairs'][0]['PublicKey'])
        for key in key['KeyPairs']: #returve the public key to add to user
            if key['KeyName'] == key_name: public_key = key['PublicKey']
        print(public_key)
        return public_key

    #create a sercurity group
    def create_security_group(self):
        security_group = self.sg_wrapper.create(self.sg_group_name, "Security group for the new instance.")
        ip_response = urllib.request.urlopen('http://checkip.amazonaws.com')
        current_ip_address = ip_response.read().decode('utf-8').strip()
        response = self.sg_wrapper.authorize_ingress(current_ip_address)
        if response['Return']:
            print("Security group rules updated.")
        else:
            print("Couldn't update security group rules.")
        self.sg_wrapper.describe()


    #create the EC2 instance
    def create_instance(self):
        user1_name = self.user_config[0]['login']#user1
        user2_name = self.user_config[1]['login']#user2
        #generate the key pairs
        user1_key = self.create_key_pair(key_name=user1_name) 
        user2_key = self.create_key_pair(key_name=user2_name)
        #Script to run in the VM on boot to create and ssh keys to the users 
        user_data = """#!/bin/bash
            sudo mkdir /data
            sudo mkfs.ext4 %(disk_name)s 
            sudo sudo mount %(disk_name)s %(mount_path)s  -t ext4
            sudo adduser %(user1_name)s
            sudo mkdir /home/user1/.ssh
            sudo touch /home/user1/.ssh/authorized_keys
            sudo echo %(key1)s > /home/user1/.ssh/authorized_keys
            sudo adduser %(user2_name)s
            sudo mkdir /home/user2/.ssh
            sudo touch /home/user2/.ssh/authorized_keys
            sudo echo %(key2)s > /home/user2/.ssh/authorized_keys
            """ % {'disk_name': self.disk_config[1]['device'],
                'mount_path': self.disk_config[1]['mount'],
                'user1_name': user1_name, 'key1': user1_key,
                'user2_name': user2_name, 'key2': user2_key}

        architecture = self.server_config['architecture']
        virtualization_type = self.server_config['virtualization_type']
        instance_type = self.server_config['instance_type']

        ssm_client = boto3.client('ssm', region_name="us-east-2")
        ami_paginator = ssm_client.get_paginator('get_parameters_by_path')
        ami_options = []
        ##Retrive the image id from the config

        for page in ami_paginator.paginate(Path='/aws/service/ami-amazon-linux-latest'):
            ami_options += page['Parameters']

        amzn2_images = self.inst_wrapper.get_images(
            [opt['Value'] for opt in ami_options if self.server_config['ami_type'] in opt['Name']])

        image =  ""
        for i in amzn2_images: 
            if i.virtualization_type == virtualization_type and i.architecture == architecture: image = i

        inst_types = self.inst_wrapper.get_instance_types(image.architecture)

        if instance_type not in list(i['InstanceType'] for i in inst_types): print( "The selected Instance Type does not exist with for the desired configuration")
        # create the instance
        self.inst_wrapper.create(
                image,
                instance_type, self.key_pair_obj.key_pair, user_data, self.disk_config, self.server_config['min_count'], self.server_config['max_count'], [self.sg_wrapper.security_group])
                
        print(self.inst_wrapper.display())
        print(f"Your instance is ready")
        print("instance ID:", self.inst_wrapper.instance.id)

        print("Run this to shh into the instance:")

        print('ssh -i "{}.pem" {}@{}'.format(user1_name, user1_name, self.inst_wrapper.instance.public_ip_address))
        print('ssh -i "{}.pem" {}@{}'.format(user2_name, user2_name, self.inst_wrapper.instance.public_ip_address))

    def cleanup(self):
        self.inst_wrapper.terminate()
        print("Deleted instance.")
        self.sg_wrapper.delete()
        print("Deleted security group.")
        


if __name__ == '__main__':
    ##read the ymal config file
    
    with open("config.yaml", "r") as stream:
        try:
            configurations = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    #process the yaml data
    server_config = configurations['server']
    disk_config = server_config['volumes']
    user_config = server_config['users']
    server_config.pop('volumes', None)
    server_config.pop('users', None)
    #intiate the class
    sol = Solution('isnt-sg-group', server_config, disk_config, user_config)  
    #call the functions
    sol.create_security_group()#create the security group
    sol.create_instance()#create the EC2 insstance
    # sol.cleanup()
