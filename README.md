# nextcord-bot
CrazyCo Management bot

## Overview

This Discord bot provides various functionalities, including custom commands, captcha verification, guild settings management, and some test commands.

## Prerequisites

1. **Python**: Ensure you have Python installed (preferably Python 3.8+).
2. **Discord Bot Token**: Create a Discord bot via the Discord Developer Portal and get its token.
3. **MySQL Database**: Set up a MySQL database for the bot to connect to.

## Setup

1. **Clone/Download the Bot**:
   - Download or clone the bot repository to your local machine.

2. **Install Dependencies**:
   - Navigate to the bot directory and install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Environment Variables**:
   - Create a `.env` file in the bot directory and add the following variables:
     ```
     DISCORD_TOKEN=your_discord_bot_token
     DB_HOST=your_database_host
     DB_USER=your_database_user
     DB_PASSWORD=your_database_password
     DB_NAME=your_database_name
     ```

4. **Run the Bot**:
   - Start the bot by running the `bot.py` script:
     ```bash
     python bot.py
     ```

## Bot Commands and Features

### Custom Commands

Allows administrators to add custom commands that respond with predefined messages.

- **Add Custom Command**:
  - Command: `!addcommand <command_name> <response>`
  - Permissions: Requires the user to have administrator permissions.
  - Function: Adds a custom command to the bot that responds with a specified message.

### Captcha Verification

Ensures new members complete a captcha verification process before fully joining the server. Automatically assigns a captcha role and kicks members who fail to complete the captcha in time.

### Guild Settings Management

Provides commands to manage guild-specific settings, including listing and managing guild administrators.

- **List Guild Admins**:
  - Command: `/guild admins list`
  - Description: Lists the current guild admins.
  - Permissions Check: Checks if the user has the necessary permissions.
  - Response: Sends an embedded message with the list of guild admins.

### Test Commands

Includes simple commands to verify the bot's responsiveness and functionality.

- **Test Command**:
  - Command: `/test`
  - Description: A simple test command to check if the bot is responsive.
  - Response: Sends a message "test response" when invoked.

- **Human Rights Command**:
  - Command: `/human_rights`
  - Description: A whimsical command asking if the bot believes in human rights.
  - Response: Sends a specific image URL as a response.

### Event Listeners

Reacts to member join events, applying necessary roles and enforcing captcha verification.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.c

