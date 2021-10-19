# BerrylliumAPI

## What is it?

The BerrylliumAPI is the pivotal element of the Berryllium project, designed to run in the local network on the
Raspberry Pi. It provides an application programming interface that lets the users interact with a database via http
requests. Those users can be, on the one hand, services which collect information and send it to the API (like
[SeleniumMarks](https://github.com/AlecGhost/SeleniumMarks)) and on the other hand, client programmes that process or
display this data (like [BerrylliumMobile](https://github.com/AlecGhost/BerrylliumMobile)).

## Documentation

The data is stored as "messages", containing not only the json message itself, but also some metadata. It is structured
as follows:

- Message
  - id
  - sender
  - subject
  - timestamp
  - json message

To view any messages one must have a user account with a username and an api key. More on this
on [Adding Users](#adding-users). They must be provided as named parameters in the http request.

### API

#### GET Requests

To get messages the following parameters at the end of the url must be provided:
> ?username=[your username]&api-key=[your api key]

Get all available messages:
> /messages

Get one specific message by id:
> /messages/[id]

Get the latest message:
> /messages/latest

Get all of todays messages:
> /messages/today

Get all archived messages:

> /messages/archived-messages

#### POST Requests

To post a message, not only username and password must be provided as http parameters, but also the subject:
> ?username=[your username]&api-key=[your api key]&subject=[message's subject]

Post new message:
> /add

#### DELETE Requests

To delete a messages the following parameters at the end of the url must be provided:
> ?username=[your username]&api-key=[your api key]

Delete a message by id:
> /messages/[id]/delete

### Adding Users

To add a user, run the file "add_user.py". It is a command line application that asks for the desired username and api
key. After entering them, the key gets hashed and both are stored in the database.

## Dependencies

- [Flask](https://github.com/pallets/flask)
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy)
- [bcrypt](https://github.com/pyca/bcrypt)
