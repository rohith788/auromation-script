# Fetch Rewards DevOps take home

You can create the credintials(access key and secret key) by following the instructions here : 
https://docs.aws.amazon.com/toolkit-for-eclipse/v1/user-guide/setup-credentials.html

You can follow the instructions on the link below to set up the AWS credentials.
Setup AWS credintials (make sure you get the credentials for the root user): https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html

>export AWS_ACCESS_KEY_ID=<your_access_key_id>

>export AWS_SECRET_ACCESS_KEY=<your_secret_access_key>

>export AWS_REGION=<your_aws_region>

## Set up python dependencies
Make sure you have python3 and pip installed before this step.

Install the dependecies necessary for this projet using the code below. Use "pip" or "pip3" based on what package is installed on your system.

    pip/pip3 install btot3
    pip3/pip install pyyaml


The SSH key pair will be generated when the code is run and the client key will be stored in the directory of the code for both the users. 




Expain why scripts

ssh -i user1_key_pair.pem ec2-user@ec2-a-b-c-d.us-west-2.compute.amazonaws.com


