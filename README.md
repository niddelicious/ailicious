# ailicious
Twitch chatbot hooked up to OpenAI API ChatGPT 3.5

The bot will show up in chat as __botdelicious__ *(unless otherwise specified in the config file)*


# Request bot to join your channel
If you want to use the bot in your channel, but don't want to host it yourself, please send the author a message on Discord to request to be added to the bot's channel list.
https://discord.gg/Eg9nZhtMWT 

And OpenAI API key and Organization will be required.


## OpenAI API key
You will be asked to provide your own OpanAI API key, which you can get for free here: https://beta.openai.com/
Using the bot will cost you $0.002 per 1000 tokens.
Depending on your settings chatting with the bot can cost about 300 tokens per message when a conversation is continuing.
Signing up will grant you a credit amount with an expiration date that is listed on your Usage page.
You will then be billed for your usage per calendar month.

Organization ID is listed on the Organization > Settings page.

An API key can be generated on the User > API keys page.


## Twitch Application Credentials (for running your own bot)
You will need a client_id and client_secret to use the Twitch API, which is a requirement to run the chat integration of the bot. You can get these by creating a Twitch application here: https://dev.twitch.tv/console

Once you have your credentials you will also need a Refresh Token. The simplest way to get one is to follow the instructions on the Twitch Token Generator website: https://twitchtokengenerator.com/

This is not recommended for anything other than testing or development purposes. For production purposes you should set up a proper callback for getting tokens.


# Settings
- OpenAI API key: Your OpenAI API key
- OpenAI Organization ID: Your OpenAI Organization ID
- Prompt: The message you will request the bot to act like
- Thinking message: The message the bot will send while it is thinking
- Error message: The message the bot will send if it encounters an error
- Memory: The number of messages the bot will remember
- Chat level: The level required to chat with the bot. Viewer, VIP, Subscriber, Moderator, Broadcaster
- Shoutouts: If the bot should respond to !so commands
- Shoutout level: The level required to trigger shoutouts.  Viewer, VIP, Subscriber, Moderator, Broadcaster

# System operations
After creating a config.ini file, according to the config.ini-example, you can start the bot by running the main.py script.
The script will log debug information to console, and connect to Twitch chat using the credentials provided in the config.ini file. Before logging in to Twitch it will automatically update the access token using the credentials and refresh token provided in the config.ini file.
Once logged in it will update the access token every hour.

When the application is running, you can use a few Command Line commands to control the bot.


# Chat operations
## Chatting
Messaging the bot directly, using __*@botdelicious*__ at the start of the message, will prompt it to respond. It will save the incoming message to memory and use it in the conversation log sent to OpenAI to generate a response.

## Shoutouts
Using "!so <username>" will trigger a shoutout to the specified user. The bot will fetch the user's stream title, game, tags, About section, and if they are currently streaming, and then use this data to generate an appropriate shoutout message, including a link to the user's channel.

# CLI Commands
- start <module>: Starts a module (only twitch_chat for now)
- status: Lists all modules and their status
- stop <module>: Stops a module (only twitch_chat for now)
- join <channel>: Joins a twitch channel (channel must be configured in config.ini)
- leave <channel>: Leaves a twitch channel
- list: Lists all channels the bot is currently logged into 
- update: Reloads the config file, which allows for new channels to be configured while the app is running
- connect all: Joins all channels configured in config.ini and have been loaded
- configured: Lists all configured sections, aka channels (including twitch chat)
- exit: Stops all modules and exits the program