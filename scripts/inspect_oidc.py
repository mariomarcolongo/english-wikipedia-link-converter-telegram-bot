"""Print selected public identity claims, never the OIDC or request token."""

import base64
import json
import os
import urllib.parse
import urllib.request

PUBLIC_CLAIMS = (
    "iss", "aud", "sub", "repository", "repository_id",
    "repository_owner_id", "ref", "environment",
)


def main() -> None:
    url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
    separator = "&" if "?" in url else "?"
    url += separator + urllib.parse.urlencode({"audience": "sts.amazonaws.com"})
    request = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"],
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        encoded = json.loads(response.read())["value"].split(".")[1]
    payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    print(json.dumps({key: payload[key] for key in PUBLIC_CLAIMS if key in payload}, sort_keys=True))


if __name__ == "__main__":
    main()
