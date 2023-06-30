helps = [
       {
        "title"   : "Getting a Telegram Bot Token",
        "content" : """1. Open the Telegram app or visit the Telegram website (web.telegram.org) and log in to your account.
2. In the Telegram app, search for the "BotFather" bot. If you're using the Telegram website, click on the search bar and type "BotFather" to find the bot.
3. Open the chat with BotFather and click on the Start button or send a message saying "/start" to initiate the conversation.
4. Once the chat with BotFather is active, send the command "/newbot" to create a new bot. Follow the instructions provided by BotFather.
5. Choose a name for your bot. This name will be displayed in chats and conversations.
6. After selecting a name, BotFather will provide you with a unique bot token. The token will be a long string of characters, typically in the format `123456789:ABCdefGHIJKlmnOpqrSTUvwxYZ`.
7. Save the bot token in a secure location. It will be required to authenticate and interact with your Telegram bot."""
    },
    {
        "title"   : "Getting File IDs",
        "content" : """You can get file's id with built-in commands:
1. /get_file_id: To retrieve the file ID for a specific media file, follow these steps:
- Send the media file (e.g., an image, video, or document) to your Telegram bot.
- Include the `/get_file_id` command as the caption of the media file. Type it directly as the caption or use the "Add caption" feature in your Telegram app.
- Please note that the `/get_file_id` command can only be used by admins of the software.
- The bot will process the media file and respond with a message containing the file ID of the media you just sent.
2. /get_all_ids: To enable automatic retrieval of file IDs for all subsequent media files, follow these steps:
- Send the command `/get_all_ids` to your Telegram bot.
- From this point forward, whenever you send media files to your bot, it will automatically respond with their corresponding file IDs.
- Only admins have the authorization to use the `/get_all_ids` command.
- The automatic file ID retrieval will continue until you disable it using the command `/get_all_ids` again."""
    },
]