import argparse
from db import add_api_key

# Create the CLI parser
def main():
    parser = argparse.ArgumentParser(description='Manage API keys for the Grok-Api sub-project.')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Create the 'generate' command
    generate_parser = subparsers.add_parser('generate', help='Generate a new API key')
    generate_parser.add_argument('--expiration-days', type=int, help='Number of days before the API key expires')

    # Parse the arguments
    args = parser.parse_args()

    # Handle the 'generate' command
    if args.command == 'generate':
        api_key = add_api_key(args.expiration_days)
        print(f"New API key generated: {api_key}")

if __name__ == '__main__':
    main()