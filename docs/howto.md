# How-tos

### Remove an account from an account file

Manual editing of the accounts file can be done by first decrypting the config:

    pyggybank accounts > decrypted_accounts.DELME.yml

Making the necessary changes, and then piping these back in with:

    pyggybank accounts < decrypted_accounts.DELME.yml

