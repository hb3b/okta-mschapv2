from flask import Flask, request, jsonify
import requests
import os
import hashlib

app = Flask(__name__)


@app.route('/Users/<okta_user>', methods=["PATCH"])
def patch_user(okta_user):
    message = request.json

    if message.get('schemas') == ['urn:ietf:params:scim:api:messages:2.0:PatchOp']:
        if message.get('Operations')[0]['op'] == 'replace' and \
         'password' in message.get('Operations')[0]['value'].keys():
            password = message.get('Operations')[0]['value']['password']
            hashed_password = hashlib.new("md4", password.encode("utf-16le")).hexdigest()

            api_key = os.environ['okta_token']
            headers = {'Authorization': f"SSWS {api_key}"}
            profile = {'profile': {'ntPassword': hashed_password}}
            requests.post(f'https://company.okta.com/api/v1/users/{okta_user}', headers=headers, json=profile)

    return ('', 204)


@app.route('/Users/<okta_user>', methods=["GET"])
def get_user(okta_user):
    user = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": okta_user,
        "userName": okta_user,
        "active": True,
    }

    return jsonify(user)


@app.route('/Users', methods=["GET"])
def list_users():
#    Uncomment this section when initially configuring the SCIM app
#    return jsonify({
#        "totalResults": 0,
#        "itemsPerPage": 0,
#        "schemas": [
#            "urn:scim:schemas:core:2.0"
#        ],
#        "Resources": []
#    })
    if 'filter' in request.args:
        if request.args.get('filter').startswith('userName eq'):
            okta_user = request.args.get('filter')[13:-1]
            users = {
                "totalResults": 1,
                "itemsPerPage": 1,
                "startIndex": 1,
                "schemas": [
                    "urn:scim:schemas:core:2.0"
                ],
                "Resources":
                [
                    {
                        "schemas": [
                            "urn:scim:schemas:core:2.0"
                        ],
                        "id": okta_user,
                        "active": True,
                    }
                ]
            }
    else:
        # in case someone hits the "import" button by accident
        return ('', 401)

    return jsonify(users)


@app.route('/authorize/<okta_user>', methods=["GET"])
def get_nt_password(okta_user):
    api_key = os.environ['okta_token']
    headers = {'Authorization': f"SSWS {api_key}"}
    r = requests.get(f'https://company.okta.com/api/v1/users/{okta_user}', headers=headers)
    j = r.json()
    if r.status_code == 200:
        if 'ntPassword' in j['profile']:
            if j['profile']['ntPassword']:
                return jsonify({'control:NT-Password': j['profile']['ntPassword']})

    return jsonify({})
