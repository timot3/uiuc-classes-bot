# A Discord Bot for UIUC Classes
Inspired by [Professor Wade Fagen-Ulmschneider's Reddit bot](https://github.com/illinois/reddit-uiuc-bot/)

First, add this bot to your discord server (or click the "add to server" button in Discord to add the bot to your server):
https://discord.com/api/oauth2/authorize?client_id=710426023224934490&permissions=0&scope=bot
The bot needs permissions to read messages, send messages, and embed links. I don't auto-grant these 
permissions in the link so that moderators can decide what channels to give these permissions in.

### To get a class: 
`['department''class number']`. This command is case-insensitive.


Alternatively, `c$search <query>` also works. This is powered by my own [UIUC course API](https://github.com/timot3/uiuc-course-api).

Example:
![cs225](https://media.discordapp.net/attachments/735523773515694149/791889935607136266/unknown.png)

You can request multiple classes on the same line as well.

![two-classes](https://media.discordapp.net/attachments/735523773515694149/791889705687973928/unknown.png)

The bot and API run on separate Heroku Dynos.

Currently I have my own container running on an AWS t2.micro instance.

### TODO:
- Switch to [UIUC Classes API](https://uiuc-api.readthedocs.io/en/latest/)



