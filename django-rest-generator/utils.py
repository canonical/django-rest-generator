import re
def sanitize_endpoint_to_method_name(endpoint):
    endpoint = str(endpoint).lower().strip()
    endpoint = re.sub(r"{.*}\/", "", endpoint)
    endpoint = endpoint.replace("/", ".")
    if endpoint.endswith("."):
        endpoint = endpoint[:-1]
    return endpoint