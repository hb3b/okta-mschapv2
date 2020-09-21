# okta-mschapv2

This is a small Okta SCIM app that watches for password changes and then re-hashes them from cleartext to NT format. NT hashes are in turn stored within the user profile and accessible by systems like FreeRADIUS. This script is helpful for supporting protocols that do client-side hashing and server-side comparisons like IKEv2 + EAP-MSCHAPv2 or 802.1x + EAP-PEAP-MSCHAPv2.

### FreeRADIUS
The `/authorize/<okta_user>` route is intended to work with the FreeRADIUS rest module.

```
authorize {
    uri = "http://127.0.0.1:5000/authorize/%{User-Name}"
    method = 'get'
    tls = ${..tls}
}
```
