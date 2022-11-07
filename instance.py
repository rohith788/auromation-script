import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class InstanceWrapper:
    def __init__(self, ec2_resource, instance=None):
        self.ec2_resource = ec2_resource #this holds the ec2 resource
        self.instance = instance

    @classmethod
    def from_resource(cls):
        ec2_resource = boto3.resource('ec2', region_name="us-east-2")
        return cls(ec2_resource)

    def create(self, image, instance_type, key_pair, user_data, disk_config, min, max ,security_groups=None):
        #crete and start the Ec2 instance
        try:
            BlockDeviceMappings=[
                {
                'DeviceName': disk_config[0]['device'],
                'Ebs': {
                    'DeleteOnTermination': True,
                    'VolumeSize': disk_config[0]['size_gb'],
                    'VolumeType': disk_config[0]['type']
                    }
                },
                {
                'DeviceName': disk_config[1]['device'],
                'Ebs': {
                    'DeleteOnTermination': True,
                    'VolumeSize': disk_config[1]['size_gb'],
                    'VolumeType': disk_config[1]['type'],
                    }
                }
            ]
            instance_params = {
                'ImageId': image.id, 
                'InstanceType': instance_type, 
                'KeyName': key_pair.name, 
                'Placement': {'AvailabilityZone': 'us-east-2a'}, 
                'UserData': user_data, 
                'BlockDeviceMappings': BlockDeviceMappings
            } #the parameters of the instance
            if security_groups is not None:
                instance_params['SecurityGroupIds'] = [sg.id for sg in security_groups] #sercurity group id
            self.instance = self.ec2_resource.create_instances(**instance_params, MinCount=min, MaxCount=max)[0]
            self.instance.wait_until_running() # start the VM
        except ClientError as err:
            logging.error(
                "Couldn't create instance with image %s, instance type %s, and key %s. "
                "Here's why: %s: %s", image.id, instance_type, key_pair.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return self.instance

    def display(self, indent=1):
        if self.instance is None:
            logger.info("No instance to display.")
            return

        try:
            self.instance.load() #display the vm params
            ind = '\t'*indent
            print(f"{ind}ID: {self.instance.id}")
            print(f"{ind}Image ID: {self.instance.image_id}")
            print(f"{ind}Instance type: {self.instance.instance_type}")
            print(f"{ind}Key name: {self.instance.key_name}")
            print(f"{ind}VPC ID: {self.instance.vpc_id}")
            print(f"{ind}Public IP: {self.instance.public_ip_address}")
            print(f"{ind}State: {self.instance.state['Name']}")
            client = boto3.client('ec2', region_name="us-east-2")
            client.get_console_output(InstanceId=self.instance.id)
        except ClientError as err:
            logger.error(
                "Couldn't display your instance. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def terminate(self):
        if self.instance is None:
            logger.info("No instance to terminate.")
            return

        instance_id = self.instance.id
        try:
            self.instance.terminate() #terminated the VM
            self.instance.wait_until_terminated() #waits for the VM to terminate
            self.instance = None
            print('instance terminated')
        except ClientError as err:
            logging.error(
                "Couldn't terminate instance %s. Here's why: %s: %s", instance_id,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def start(self):
        if self.instance is None:
            logger.info("No instance to start.")
            return
        try:
            response = self.instance.start() #start VM
            self.instance.wait_until_running()
        except ClientError as err:
            logger.error(
                "Couldn't start instance %s. Here's why: %s: %s", self.instance.id,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response

    def stop(self):
        if self.instance is None:
            logger.info("No instance to stop.")
            return

        try:
            response = self.instance.stop() #stoping the VM
            self.instance.wait_until_stopped() #waiting for the VM to stop
        except ClientError as err:
            logger.error(
                "Couldn't stop instance %s. Here's why: %s: %s", self.instance.id,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response
    
    def get_images(self, image_ids):
        try:
            images = list(self.ec2_resource.images.filter(ImageIds=image_ids)) #list Vm ids
        except ClientError as err:
            logger.error(
                "Couldn't get images. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return images

    def get_instance_types(self, architecture):
        try:
            inst_types = []
            it_paginator = self.ec2_resource.meta.client.get_paginator('describe_instance_types')
            for page in it_paginator.paginate(
                    Filters=[{
                        'Name': 'processor-info.supported-architecture', 'Values': [architecture]},
                        {'Name': 'instance-type', 'Values': ['*.micro', '*.small']}]):
                inst_types += page['InstanceTypes']
        except ClientError as err:
            logger.error(
                "Couldn't get instance types. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return inst_types
    
    def attach_role(self, arn, inst_prof, instance_id):
        client = boto3.client('ec2', region_name="us-east-2")
        IAMclient = boto3.resource('iam', region_name="us-east-2")
        waiter = IAMclient.get_waiter('instance_profile_exists')
        waiter.wait(
            InstanceProfileName=inst_prof,
            WaiterConfig={
                'Delay': 60,
                'MaxAttempts': 10
            }
        )
        response = client.associate_iam_instance_profile(
            IamInstanceProfile={
                'Arn': arn,
                'Name': inst_prof
            },
            InstanceId=instance_id
        )
        print('IAM role attached to Instance')
        return attach_role
