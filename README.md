## Current Setup
The current setup for this user authentication system are accounts that uses email and password. Here are some information that may be useful when adapting for actual projects:

- Email address validation not implemented
- Simple hashing of email and password for verification
- Account types (user & admin)
- Session structure: `session = {'acc_type': <0|1|2>, 'acc_id':<id>}`
- Database schema for simple login included (sqlite)
- Login token for app usage