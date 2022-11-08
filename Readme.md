# Fetch Rewards DevOps take home

You can create the credintials(access key and secret key) by following the instructions here : 
https://docs.aws.amazon.com/toolkit-for-eclipse/v1/user-guide/setup-credentials.html.

Although you can create an IAM user with the necessary permissions for this excercise adn use its credentials. I am using the root user credentials here. These are the instructions to user that.

1) Open the IAM Dashboard and click on the "Manage access  keys" for the root userm as shown in the image below.

2)In the Access Keys tab in the next screen, click on the "Create New Access Key" button.

3) The popup menu will have the Access Key and the Secret Key. You can also download this information in a .csv file with the "Download Key File"


You can follow the instructions on the link below to set up the AWS credentials on your local machine.(make sure you get the credentials for the root user): https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html

>   export AWS_ACCESS_KEY_ID=<your_access_key_id>

>   export AWS_SECRET_ACCESS_KEY=<your_secret_access_key>

## Set up python dependencies
Make sure you have python3 and pip installed before this step. This step will vary based on the OS you are using.

Install the dependecies necessary for this projet using the code below. Use "pip" or "pip3" based on what package is installed on your system.

    pip/pip3 install boto3
    pip/pip3 install pyyaml

## Run the Script

1) You can run the script by typing the following command

        python3 main.py

2) The should set up the the EC2 isntance with the specified configurations.

3) The script will create new SSH key pairs for both the users as shows below. Both the keys will not be editable.

4) Once the script runs sucessfully, you can run the ssh command as shown in the output terminal.
        
        ssh -i <user1-name>.pem <user1-name>@<public_ip_address>
        ssh -i <user2-name>.pem <user2-name>@<public_ip_address>

5) Once ssh-ed into the User account, you can view the volumes attached and mounted to the instance with the following command

        ldblk

6) You can change the configuration for the instance and other details by making changes to the config.yaml file. But, make sure you only make changes to the values and not the keys.

### Notes

* If you you encounter any errors reagarding the AWS credentials once you run the script, make sure you entered the correct credentials in the first part of this document.

* Sometime, the users might not be ready to login to immediately. So if you face a permission denied error, try again after a few minutes. 