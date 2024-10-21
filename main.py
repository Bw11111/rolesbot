import discord
from discord import app_commands
from discord.ext import commands
from better_profanity import profanity
import re

# Define the intents
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.members = True

# Set your bot's prefix here
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize the profanity filter
profanity.load_censor_words()

# Regular expression to match valid hex color codes
HEX_COLOR_REGEX = r'^#(?:[0-9a-fA-F]{3}){1,2}$'

@bot.event
async def on_ready():
    # Sync the slash commands with Discord
    await bot.tree.sync()
    print(f'Bot is ready! Logged in as {bot.user.name}')

# Slash command for users to create a role with a specific hex color
@bot.tree.command(name="create_role", description="Create or assign a custom role with a specified color")
async def create_role(interaction: discord.Interaction, color_hex: str):
    # Check if the color hex is valid
    if not re.match(HEX_COLOR_REGEX, color_hex):
        await interaction.response.send_message("Invalid hex color code! Please provide a valid hex code (e.g. #ff5733).", ephemeral=True)
        return

    # Check if the role name contains profanity (in case of some edge cases)
    if profanity.contains_profanity(color_hex):
        await interaction.response.send_message("Please avoid using inappropriate words for the hex code.", ephemeral=True)
        return

    # Check if a role with the same hex code already exists
    existing_role = discord.utils.get(interaction.guild.roles, name=color_hex)
    if existing_role:
        # Check if the role has no special permissions
        if existing_role.permissions == discord.Permissions.none():
            # Assign the existing role to the user
            await interaction.user.add_roles(existing_role)
            await interaction.response.send_message(f"Role `{color_hex}` already exists and has been assigned to you!")
            return
        else:
            await interaction.response.send_message(f"A role with the color `{color_hex}` exists but has special permissions. Cannot assign it.", ephemeral=True)
            return

    try:
        # Create the role with the hex code as the name and color
        color = discord.Color(int(color_hex.strip("#"), 16))
        new_role = await interaction.guild.create_role(name=color_hex, color=color, permissions=discord.Permissions.none())
        # Assign the role to the user
        await interaction.user.add_roles(new_role)
        await interaction.response.send_message(f"Role `{color_hex}` created with color `{color_hex}` and assigned to you!")
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to create roles. Please ensure I have the 'Manage Roles' permission.", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("Something went wrong while creating the role.", ephemeral=True)


@bot.tree.command(name="remove_role", description="Remove a color role (based on hex code) from yourself")
async def remove_role(interaction: discord.Interaction):
    roles_to_remove = []


    for role in interaction.user.roles:
        if re.match(HEX_COLOR_REGEX, role.name):
            roles_to_remove.append(role)

    if roles_to_remove:
        try:
            await interaction.user.remove_roles(*roles_to_remove)
            await interaction.response.send_message(f"Removed the color roles: {', '.join([role.name for role in roles_to_remove])}")
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to remove roles.", ephemeral=True)
    else:
        await interaction.response.send_message("You don't have any color roles to remove.", ephemeral=True)

bot.run('')
