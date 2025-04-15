import os
import ssl
import certifi

def configure_ssl():
    # Set the SSL certificate path to use certifi's certificates
    os.environ['SSL_CERT_FILE'] = certifi.where()
    
    # Create a custom SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.load_verify_locations(cafile=certifi.where())
    
    return ssl_context 