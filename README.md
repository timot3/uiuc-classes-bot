# UIUC Discord Classes Bot
Inspired by [Professor Wade Fagen-Ulmschneider's Reddit bot](https://github.com/illinois/reddit-uiuc-bot/blob/master/process_reddit_post.py)

To request a class, first add this bot to your discord server:
https://discord.com/api/oauth2/authorize?client_id=710426023224934490&permissions=0&scope=bot

### To get a class: 
`['college''class number']`. 
Example: [cs 225] returns 
```
CS225
Credit hours: 4 hours.
Average GPA: 3.22
Data abstractions: elementary data structures (lists, stacks, queues, and trees) and their implementation using an object-oriented programming language. Solutions to a variety of computational problems such as search on graphs and trees. Elementary analysis of algorithms. Prerequisite: CS 125 or ECE 220; One of CS 173, MATH 213, MATH 347, MATH 412 or MATH 413.
```

The docker container is available [here](https://hub.docker.com/r/timot3/uiuc-classes). 
Currently I have it running on an AWS t2.micro instance.

This command is case-insensitive.