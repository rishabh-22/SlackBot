# SlackBot
#### This repository holds the code for a slackbot which applies for leaves on your behalf.

The bot is built using python and uses MongoDB at the backend. You can give your command to slackbot in a specific format and it will mark your leave in the database and upon successful marking, send a notification in the specified channel about your absence with its duration. Else it will return you with the error you might have made while passing the command. 

## The bot currently offers 3 commands. 

`help` : this will return will the basics of using the slackbot and how to use the commands.

`check` : it will fetch your leaves from the database and display them.

`apply` : this command is used to apply for leaves based on user input format. (refer to help for more)

### How to install and use:

Fork or clone the repository. Create a virtual environment and activate it.

```
pip install -r requirements.txt

python main.py
```

For slack integration, you will need a bot, an `ACCESS_TOKEN` for bot and an `AUTH_TOKEN` with scopes which allow access for:

View profile details about people in the workspace : `users.profile:read`

View email addresses of people in the workspace : `users:read.email`

and add your bot to the specified channel you want it to send leave notification to.

And of course MongoDB. (locally or hosted)


##### Hope you like it. :D
