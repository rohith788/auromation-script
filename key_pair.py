import logging
import os
import tempfile
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class KeyPairWrapper:
    def __init__(self, ec2_resource, key_file_dir, key_pair=None):
        self.ec2_resource = ec2_resource
        self.key_pair = key_pair 
        self.key_file_path = None 
        self.key_file_dir = key_file_dir #folder to store the KeyPair

    @classmethod
    def from_resource(cls):
        ec2_resource = boto3.resource('ec2', region_name="us-east-2") #using ec2 
        return cls(ec2_resource, tempfile.TemporaryDirectory())

    def create(self, key_name):
        try:
            self.key_pair = self.ec2_resource.create_key_pair(KeyName=key_name) #creating a new key pair with the ec2 resource 
            self.key_file_path = os.path.join(self.key_file_dir.name, f'{self.key_pair.name}.pem') #file path name
            print('key stored at : ', self.key_file_path)
            with open(self.key_file_path, 'w') as key_file:
                key_file.write(self.key_pair.key_material) #opening and writing the key
            #save the key pair to local machine
            private_key_file=open(f'{self.key_pair.name}.pem',"w")
            private_key_file.write(self.key_pair.key_material)
            private_key_file.close
        except ClientError as err: #error if the key cannot be created
            logger.error(
                "Couldn't create key %s. Here's why: %s: %s", key_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return self.key_pair

    def list(self, limit):
        try:
            for kp in self.ec2_resource.key_pairs.limit(limit): #limit the number of key pairs displayed
                #printing the key information
                print(f"Found {kp.key_type} key {kp.name} with fingerprint:")
                print(f"\t{kp.key_fingerprint}")
        except ClientError as err: #error message if the key isn't created
            logger.error(
                "Couldn't list key pairs. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def delete(self, key_name=None):
        if self.key_pair is None: # if there are no key pairs
            logger.info("No key pair to delete.")
            return
        key_name = self.key_pair.name if self.key_pair.name else key_name #name of the key pair
        try:
            self.key_pair.delete() #delete the key
            self.key_pair = None # change the value to empty
            print("Key Pair deleted")
        except ClientError as err: #error if the key dosn't get deleted
            logger.error(
                "Couldn't delete key %s. Here's why: %s : %s", key_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise