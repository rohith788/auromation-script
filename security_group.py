import logging
from pprint import pp
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class SecurityGroupWrapper:
    def __init__(self, ec2_resource, security_group=None):
        self.ec2_resource = ec2_resource
        self.security_group = security_group

    @classmethod
    def from_resource(cls):
        ec2_resource = boto3.resource('ec2', region_name="us-east-2")
        return cls(ec2_resource)

    def create(self, group_name, group_description):
        try:
            self.security_group = self.ec2_resource.create_security_group(
                GroupName=group_name, Description=group_description)
        except ClientError as err:
            logger.error(
                "Couldn't create security group %s. Here's why: %s: %s", group_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return self.security_group

    def authorize_ingress(self, ssh_ingress_ip):
        if self.security_group is None:
            logger.info("No security group to update.")
            return

        try:
            ip_permissions = [{
                # SSH ingress open to only the specified IP address.
                'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
                'IpRanges': [{'CidrIp': f'{ssh_ingress_ip}/32'}]}]
            response = self.security_group.authorize_ingress(IpPermissions=ip_permissions)
        except ClientError as err:
            logger.error(
                "Couldn't authorize inbound rules for %s. Here's why: %s: %s",
                self.security_group.id,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response

    def describe(self):
        if self.security_group is None:
            logger.info("No security group to describe.")
            return

        try:
            print(f"Security group: {self.security_group.group_name}")
            print(f"\tID: {self.security_group.id}")
            print(f"\tVPC: {self.security_group.vpc_id}")
            if self.security_group.ip_permissions:
                print(f"Inbound permissions:")
                pp(self.security_group.ip_permissions)
        except ClientError as err:
            logger.error(
                "Couldn't get data for security group %s. Here's why: %s: %s", self.security_group.id,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def delete(self):
        if self.security_group is None:
            logger.info("No security group to delete.")
            return

        group_id = self.security_group.id
        try:
            self.security_group.delete()
        except ClientError as err:
            logger.error(
                "Couldn't delete security group %s. Here's why: %s: %s", group_id,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise