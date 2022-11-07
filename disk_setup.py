import logging
import os
import tempfile
import boto3
from botocore.exceptions import ClientError

class DeskSetupWrapper:
    def __init__(self, ec2client, availability_zone="us-east-2a"):
        self.availability_zone = availability_zone
        self.ec2client = ec2client
    
    @classmethod
    def from_resource(cls):
        ec2_resource = boto3.client('ec2', region_name="us-east-2") #using ec2 
        return cls(ec2_resource)


    def create(self, size, disk_type,):
        try:
            response = self.ec2client.create_volume(
                AvailabilityZone=self.availability_zone,
                Size=size
                # VolumeType=disk_type
            )
            self.vol = response
            if response['ResponseMetadata']['HTTPStatusCode']== 200:
                volume_id= response['VolumeId']
                print('***volume:', volume_id)

                self.ec2client.get_waiter('volume_available').wait(
                    VolumeIds=[volume_id],
                    # DryRun=True
                    )
                print('***Success!! volume:', volume_id, 'created...')
        except Exception as e:
            print('failed to create volume')
            print(type(e), ':', e)
    
    def mount_disk(self, device, instance_id):
        self.ec2client.attach_volume(
            Device=device,
            InstanceId=instance_id,
            VolumeId=self.vol['VolumeId'],
            )
        print('disk attached to the instance')
        
    def cleanup(self):
        ec2 = boto3.resource('ec2', region_name="us-east-2")
        try:
            for volume in ec2.volumes.all():
                print(volume.delete())
                print('volume deleted')
        except Exception as e:
            print('delete failed')
            print(type(e), ':', e)
