# A Discord Bot for UIUC Classes
Inspired by [Professor Wade Fagen-Ulmschneider's Reddit bot](https://github.com/illinois/reddit-uiuc-bot/)

First, add this bot to your discord server:
https://discord.com/api/oauth2/authorize?client_id=710426023224934490&permissions=0&scope=bot

### To get a class: 
`['department''class number']`. 
This command is case-insensitive.

Example:

![cs225](https://media.discordapp.net/attachments/735523773515694149/791889935607136266/unknown.png)

You can request multiple classes on the same line as well.

![two-classes](https://media.discordapp.net/attachments/735523773515694149/791889705687973928/unknown.png)

I have the bot running on a docker container hosted on an AWS t2.micro instance. I decided not to use their container service because the free tier option is less powerful. The docker container is available [here](https://hub.docker.com/r/timot3/uiuc-classes), but you cannot run that container without a token in your environment variables.

Currently I have my own container running on an AWS t2.micro instance.

### TODO:
- Switch to [UIUC Classes API](https://uiuc-api.readthedocs.io/en/latest/)



