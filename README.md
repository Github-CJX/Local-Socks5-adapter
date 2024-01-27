# Location Socks5 Proxy Server

## Introduction

Create a local Socks5 proxy server that connects to a remote Socks5 proxy server with or without authentication. Transform the remote connection into a local Socks5 proxy without authentication. This setup ensures the security of a private V2Ray Socks5 proxy server while enabling compatibility with browsers using the Chromium engine (Edge, as Chrome does not support authenticated Socks5 proxies). By employing the Proxy SwitchyOmega extension, specific web pages can be configured to activate the proxy, facilitating academic research without the need to constantly toggle proxy software.

## Features

- Supports both SOCKS5 authentication and non-authentication modes.
- Handles connections from SOCKS5 clients and forwards their traffic to a remote SOCKS5 proxy.
- Configurable via a `config.json` file.

## Usage

1. Install the required dependencies:

   ```bash
   pip install PySocks
   ```

2. Configure the `config.json` file with the appropriate settings:

   ```json
   {
     "REMOTE_SOCKS5_HOST": "your_remote_socks5_host",
     "REMOTE_SOCKS5_PORT": your_remote_socks5_port,
     "USERNAME": "your_username",
     "PASSWORD": "your_password"
   }
   ```

   Make sure to replace placeholders with your actual remote SOCKS5 proxy details.

3. Run the script:

   ```bash
   python socks5_proxy_server.py
   ```

4. Upon successful startup, a message box will indicate the server has started.

## Configuration

- **REMOTE_SOCKS5_HOST**: The hostname or IP address of the remote SOCKS5 proxy.
- **REMOTE_SOCKS5_PORT**: The port number of the remote SOCKS5 proxy.
- **USERNAME**: The username for SOCKS5 authentication (leave empty for non-authentication).
- **PASSWORD**: The password for SOCKS5 authentication (leave empty for non-authentication).

## Note

- This script uses the `PySocks` library to handle SOCKS5 proxy functionality.
- The server listens on `127.0.0.1:1080` by default. Adjust the `LOCAL_SOCKS5_HOST` and `LOCAL_SOCKS5_PORT` variables in the script if needed.

## Disclaimer

This script is provided for educational purposes only. Use it responsibly and comply with applicable laws and regulations. The author is not responsible for any misuse or illegal activities facilitated by this script.
