import os
import sys
import boto3

def main():
    print("Fetching API keys from AWS Parameter Store...", flush=True)
    
    # Initialize boto3 SSM client
    # It will automatically pick up your AWS credentials injected into the container
    try:
        # Fallback to us-east-1 if AWS_REGION isn't set in your environment
        region = os.getenv('AWS_REGION', 'us-east-1')
        ssm = boto3.client('ssm', region_name=region)
        
        # Fetch parameters under the path
        response = ssm.get_parameters_by_path(
            Path='/merlinai/api/',
            WithDecryption=True
        )
        
        for param in response.get('Parameters', []):
            # Extract the last part of the path and make it UPPERCASE
            # e.g., /merlinai/api/anthropic_api_key -> ANTHROPIC_API_KEY
            key_name = param['Name'].split('/')[-1].upper()
            
            # Set the environment variable for the current process
            os.environ[key_name] = param['Value']
            print(f"Successfully loaded: {key_name}", flush=True)
            
    except Exception as e:
        print(f"Error fetching parameters from AWS: {e}", flush=True)
        sys.exit(1)

    print("Starting OpenCode...", flush=True)
    
    # sys.argv contains the CMD arguments passed from the Dockerfile
    # e.g., ['/entrypoint.py', 'opencode', 'serve', '--hostname', '0.0.0.0', '--port', '4096']
    if len(sys.argv) > 1:
        # os.execvp completely replaces this Python script with the OpenCode process.
        # This keeps the container clean and passes environment variables forward.
        os.execvp(sys.argv[1], sys.argv[1:])
    else:
        print("No startup command provided.", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
