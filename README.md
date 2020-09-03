# SlackBot
#### This repository holds the code for a slackbot which applies for leaves on your behalf.

The bot is built using python and uses MongoDB at the backend. You can give your command to slackbot in a specific format and it will mark your leave in the database and upon successful marking, send a notification in the specified channel about your absence with its duration. Else it will return you with the error you might have made while passing the command. 

## The bot currently offers 3 commands. 

`help` : this will return will the basics of using the slackbot and how to use the commands.

`check` : it will fetch your leaves from the database and display them.

`apply` : this command is used to apply for leaves based on user input format. (refer to help for more)

### How to install:

Fork or clone the repository. Create a virtual environment and activate it.

```
pip install -r requirements.txt

python main.py
```

##### Hope you like it. :D
