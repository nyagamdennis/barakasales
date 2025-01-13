# Baraka-backend


This is a complete documentation on how to use this app api.

## Registering a new user

Use this url to post the register data (http://127.0.0.1:8000/users/register).

```bash
http://127.0.0.1:8000/users/register
```

## The POST request data

```Json
{
    "email":"johnd5oe@gmail.com",
    "phone_number":"0824520500566",
    "password":"1234563589"
}
```

## The Response if Daata successfully posted

```json
{
    "message": "User registered successfully!",
    "user": {
        "email": "johnd5oe@gmail.com",
        "phone_number": "0824520500566"
    }
}
```

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)