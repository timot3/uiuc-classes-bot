# A Discord Bot for UIUC Classes
Inspired by [Professor Wade Fagen-Ulmschneider's Reddit bot](https://github.com/illinois/reddit-uiuc-bot/)

First, add this bot to your discord server:
https://discord.com/api/oauth2/authorize?client_id=710426023224934490&permissions=0&scope=bot

### To get a class: 
`['department''class number']`. 
This command is case-insensitive.

Example:

![cs225](https://cdn.discordapp.com/attachments/705899037848502303/712438962647728168/unknown.png)

You can request multiple classes on the same line as well.

![two-classes](https://cdn.discordapp.com/attachments/705899037848502303/712440043154702336/two-classes.png)

### TODO:
- Make the docker container (hosted on docker hub) actually work. 
For this, I need to figure out how to use docker secrets first to not push my bot token. 

The docker container is available [here](https://hub.docker.com/r/timot3/uiuc-classes), but you cannot run that container without a config.txt file with your token.

Currently I have my own container running on an AWS t2.micro instance.

