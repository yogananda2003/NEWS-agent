import os
import certifi


def get_ca_bundle() -> str:
    """
    Corporate proxies like Zscaler/Netskope set REQUESTS_CA_BUNDLE to their
    own cert path. If that path doesn't exist on this machine, fall back to
    certifi's bundle which works for standard HTTPS calls.
    """
    for env_var in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE"):
        path = os.getenv(env_var, "")
        if path and os.path.isfile(path):
            return path

    return certifi.where()
