import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def get_parameter(parameter_name, region_name='us-east-1', with_decryption=True):
    """
    Fetches a parameter from AWS Parameter Store.

    Args:
        parameter_name (str): The name of the parameter to retrieve.
        region_name (str): AWS region where the parameter is stored.
        with_decryption (bool): Whether to decrypt the parameter value.

    Returns:
        str: The parameter value, or None if not found.
    """
    try:
        ssm = boto3.client('ssm', region_name=region_name)
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=with_decryption)
        return response['Parameter']['Value']
    except NoCredentialsError:
        print("AWS credentials not found.")
    except ClientError as e:
        print(f"Failed to retrieve parameter: {e}")
    return None

if __name__ == '__main__':
    # Example usage
    param_name = '/my/parameter/name'
    value = get_parameter(param_name)
    if value:
        print(f"Value for {param_name}: {value}")
