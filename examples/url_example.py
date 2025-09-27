"""
Example demonstrating the URL data type in confkit.

This example shows:
1. Using URL data type with validation
2. Setting and getting URL values
3. URL validation and error handling

Run with: python examples/url_example.py
"""

from configparser import ConfigParser
from pathlib import Path

from confkit import Config, URL

# Set up the parser and file
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("url_config.ini"))

# Enable automatic writing when config values are changed
Config.write_on_edit = True


class WebConfig:
    """Web application configuration with URL validation."""
    
    # Main website URL
    website_url = Config(URL("https://example.com"))
    
    # API endpoint URL
    api_endpoint = Config(URL("https://api.example.com/v1"))
    
    # Database connection URL  
    database_url = Config(URL(""))  # Optional, can be empty
    
    # FTP server URL
    ftp_server = Config(URL("ftp://ftp.example.com"))


def main():
    """Demonstrate URL data type usage."""
    print("URL Data Type Example")
    print("=" * 30)
    
    # Read initial values
    print("Initial configuration:")
    print(f"Website URL: {WebConfig.website_url}")
    print(f"API Endpoint: {WebConfig.api_endpoint}")
    print(f"Database URL: {WebConfig.database_url or 'Not configured'}")
    print(f"FTP Server: {WebConfig.ftp_server}")
    
    # Update configuration values
    print("\nUpdating configuration...")
    WebConfig.website_url = "https://mycompany.com"
    WebConfig.api_endpoint = "https://api.mycompany.com/v2"
    WebConfig.database_url = "postgresql://user:pass@localhost:5432/mydb"
    
    print("Updated configuration:")
    print(f"Website URL: {WebConfig.website_url}")
    print(f"API Endpoint: {WebConfig.api_endpoint}")
    print(f"Database URL: {WebConfig.database_url}")
    print(f"FTP Server: {WebConfig.ftp_server}")
    
    # Demonstrate URL validation
    print("\nURL Validation Examples:")
    url_type = URL()
    
    valid_urls = [
        "https://example.com",
        "http://localhost:8080",
        "ftp://files.example.com/path/file.txt",
        "mailto:user@example.com",
        "file:///home/user/document.pdf"
    ]
    
    print("Valid URLs:")
    for url in valid_urls:
        try:
            validated = url_type.convert(url)
            print(f"  ✓ {url}")
        except ValueError as e:
            print(f"  ✗ {url}: {e}")
    
    invalid_urls = [
        "not-a-url",
        "://missing-scheme",
        "example.com",  # Missing scheme
        "invalid://unsupported-scheme"
    ]
    
    print("\nInvalid URLs:")
    for url in invalid_urls:
        try:
            validated = url_type.convert(url)
            print(f"  ✓ {url}")
        except ValueError as e:
            print(f"  ✗ {url}: {e}")


if __name__ == "__main__":
    main()