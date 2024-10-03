import argparse
import yaml
import jwt


def generate_token(config_path: str) -> str:
    with open(config_path) as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)
    secret_key = config['token']
    payload = {
        'sub': next(iter(config['credentials']['usernames'])),
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def main():
    """Main function to handle command-line arguments and generate the token."""
    parser = argparse.ArgumentParser(description='Generate a JWT token.')
    parser.add_argument('--config', type=str, required=True, help='Path to the YAML configuration file.')

    args = parser.parse_args()
    try:
        token = generate_token(args.config)
        print(f"Generated Token: {token}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == '__main__':
    main()
