"""
Version: 1.0.4
Discord Bot - Golarion Calendar Tracker

Changelog:
- Ensured all commands are admin-only.
- Reviewed vulnerabilities and security in accordance with OWASP guidelines.
"""

import os
import discord
from discord.ext import commands, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pytz  # Import for timezone handling
from discord.ext.commands import has_permissions, CheckFailure

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
DATABASE_URL = "sqlite:///bot_database.db"  # SQLite database file

# Bot initialization
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
scheduler = AsyncIOScheduler()

def is_admin():
    async def predicate(ctx):
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        if ctx.author.guild_permissions.administrator:
            return True
        if admin_role and admin_role in ctx.author.roles:
            return True
        raise CheckFailure("You must be an administrator or have the @Admin role to use this command.")
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}! Ready to track Golarion dates.")
    
    if not scheduler.running:
        print("Starting the scheduler...")
        scheduler.start()
    else:
        print("Scheduler is already running.")

    # Ensure the job is scheduled to persist after restarts
    if not scheduler.get_job("daily_update"):
        scheduler.add_job(daily_update, "cron", hour=6, minute=0, timezone="UTC", id="daily_update")

    # Print scheduled jobs for verification
    for job in scheduler.get_jobs():
        print(f"Scheduled Job: {job.id}, Next Run: {job.next_run_time}")

def is_dst():
    """Determine if the current date is in Daylight Saving Time for US/Central."""
    today = datetime.now()
    # Second Sunday in March
    dst_start = datetime(today.year, 3, 8) + timedelta(days=(6 - datetime(today.year, 3, 8).weekday()))
    # First Sunday in November
    dst_end = datetime(today.year, 11, 1) + timedelta(days=(6 - datetime(today.year, 11, 1).weekday()))
    return dst_start <= today < dst_end

def get_timezone_offset():
    """Get the UTC offset for US/Central, accounting for DST."""
    return timedelta(hours=-5) if is_dst() else timedelta(hours=-6)

@scheduler.scheduled_job("cron", hour=2, minute=0, timezone="US/Central", id="daily_update")
async def daily_update():
    """Send daily Golarion date updates along with the next holiday."""
    try:
        print("Daily update triggered.")  # Debug log

        # Use US/Central time with DST adjustment
        now_utc = datetime.now(pytz.utc)
        offset = get_timezone_offset()
        current_date = now_utc + offset

        golarion_date = get_golarion_date(current_date)

        tracked_channels = session.query(TrackedChannel).all()

        for tracked in tracked_channels:
            guild = bot.get_guild(tracked.guild_id)
            if guild:
                channel = guild.get_channel(tracked.channel_id)
                if channel:
                    holiday, days_away = get_upcoming_holiday(current_date)
                    if holiday:
                        holiday_name = holiday.name
                        holiday_date = f"{GOLARION_MONTHS[holiday.month - 1]} {holiday.day}"
                        await channel.send(
                            f"Today in Golarion: {golarion_date}\n"
                            f"The next holiday is **{holiday_name}** on **{holiday_date}**, which is in **{days_away} days**."
                        )
                    else:
                        await channel.send(f"Today in Golarion: {golarion_date}\nNo upcoming holidays found.")
    except Exception as e:
        print(f"Daily update error: {e}")

# Database setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class TrackedChannel(Base):
    __tablename__ = "tracked_channels"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(Integer, nullable=False)
    channel_id = Column(Integer, nullable=False)

class GolarionHoliday(Base):
    __tablename__ = "golarion_holidays"
    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

# Create tables if they don't exist
Base.metadata.create_all(engine)

# Pathfinder Calendar Constants
GOLARION_MONTHS = [
    "Abadius", "Calistril", "Pharast", "Gozran", "Desnus", "Sarenith",
    "Erastus", "Arodus", "Rova", "Lamashan", "Neth", "Kuthona"
]
GOLARION_DAYS = ["Moonday", "Toilday", "Wealday", "Oathday", "Fireday", "Starday", "Sunday"]

# Golarion year offset (modifiable by command)
GOLARION_YEAR_OFFSET = 2697

def populate_holidays():
    """Populate the Golarion holidays table with known holidays."""
    known_holidays = [
        (1, 1, "New Year"),
        (2, 19, "Day of Bones"),
        (3, 15, "Spring Festival"),
        (4, 14, "Taxfest"),
        (6, 16, "Sunwrought Festival"),
        (8, 16, "First Brewing"),
        (10, 31, "Harvest Feast"),
        (11, 8, "Remembrance Moon"),
        (12, 25, "Winter Week")
    ]

    for month, day, name in known_holidays:
        existing_holiday = session.query(GolarionHoliday).filter_by(month=month, day=day).first()
        if not existing_holiday:
            new_holiday = GolarionHoliday(month=month, day=day, name=name)
            session.add(new_holiday)
    session.commit()

populate_holidays()

def get_holidays():
    """Retrieve all holidays from the database."""
    holidays = session.query(GolarionHoliday).all()
    return {(holiday.month, holiday.day): holiday.name for holiday in holidays}

GOLARION_HOLIDAYS = get_holidays()

def get_golarion_date(real_date: datetime) -> str:
    """Convert a real-world date to the Pathfinder/Golarion calendar date, accounting for leap years."""
    year = real_date.year + GOLARION_YEAR_OFFSET  # Adjusted to start at 4722
    month = GOLARION_MONTHS[real_date.month - 1]
    golarion_year = real_date.year + GOLARION_YEAR_OFFSET
    is_leap_year = (golarion_year >= 4724 and (golarion_year - 4724) % 4 == 0)

    day_of_month = real_date.day
    if is_leap_year and real_date.month == 2 and real_date.day == 29:
        day_of_month = 29  # Golarion leap year adds an extra day to Calistril (February)
    elif is_leap_year and real_date.month > 2:
        day_of_month += 1  # Shift all subsequent dates by one day

    day_of_week = GOLARION_DAYS[real_date.weekday()]
    holiday = GOLARION_HOLIDAYS.get((real_date.month, real_date.day), None)

    golarion_date = f"{day_of_week}, {month} {day_of_month}, {year}"
    if holiday:
        golarion_date += f" (Holiday: {holiday})"

    return golarion_date

def get_upcoming_holiday(real_date: datetime):
    """Find the nearest upcoming holiday and how many days away it is."""
    today = real_date.date()
    holidays = session.query(GolarionHoliday).all()

    # Calculate days to each holiday
    upcoming_holiday = None
    min_days_away = float('inf')
    for holiday in holidays:
        holiday_date = datetime(real_date.year, holiday.month, holiday.day).date()
        # If the holiday is earlier in the year, adjust for next year
        if holiday_date < today:
            holiday_date = datetime(real_date.year + 1, holiday.month, holiday.day).date()

        days_away = (holiday_date - today).days
        if days_away < min_days_away:
            min_days_away = days_away
            upcoming_holiday = holiday

    return upcoming_holiday, min_days_away

# Command to set the posting channel
@bot.command(name="set_channel")
@is_admin()
async def set_channel(ctx, channel: discord.TextChannel):
    """Set the channel for daily updates."""
    save_channel(ctx.guild.id, channel.id)
    await ctx.send(f"Daily updates will be posted in {channel.mention}.")

# Command to display the current channel set for daily updates
@bot.command(name="current_channel")
@is_admin()
async def current_channel(ctx):
    """Display the current channel set for daily updates."""
    tracked_channel = session.query(TrackedChannel).filter_by(guild_id=ctx.guild.id).first()
    if tracked_channel:
        channel = bot.get_channel(tracked_channel.channel_id)
        if channel:
            await ctx.send(f"Daily updates are currently set to be posted in {channel.mention}.")
        else:
            await ctx.send("The previously set channel cannot be found. Please set a new channel using `!set_channel`.")
    else:
        await ctx.send("No channel is currently set for daily updates. Use `!set_channel` to set one.")

# Command to manually post the current Golarion date
@bot.command(name="post_date")
@is_admin()
async def post_date(ctx):
    """Manually post the current Golarion date."""
    current_date = datetime.utcnow() - timedelta(hours=6)  # Convert UTC to CST
    golarion_date = get_golarion_date(current_date)
    await ctx.send(f"Today in Golarion: {golarion_date}")

# Command to display the nearest upcoming holiday
@bot.command(name="next_holiday")
@is_admin()
async def next_holiday(ctx):
    """Display the nearest upcoming holiday and how many days away it is."""
    current_date = datetime.utcnow() - timedelta(hours=6)  # Convert UTC to CST
    holiday, days_away = get_upcoming_holiday(current_date)

    if holiday:
        holiday_name = holiday.name
        holiday_date = f"{GOLARION_MONTHS[holiday.month - 1]} {holiday.day}"
        await ctx.send(f"The next holiday is **{holiday_name}** on **{holiday_date}**, which is in **{days_away} days**.")
    else:
        await ctx.send("No upcoming holidays found.")

# Command to manually change the Golarion year offset
@bot.command(name="set_year_offset")
@is_admin()
async def set_year_offset(ctx, offset: int):
    """Manually change the Golarion year offset and display the new year."""
    global GOLARION_YEAR_OFFSET
    GOLARION_YEAR_OFFSET = offset
    current_date = datetime.utcnow() - timedelta(hours=6)
    new_year = current_date.year + GOLARION_YEAR_OFFSET
    await ctx.send(f"The Golarion year offset has been updated to {GOLARION_YEAR_OFFSET}. The current Golarion year is now {new_year}.")

# Help command
@bot.command(name="calendar_help")
@is_admin()
async def help_command(ctx):
    """Display a list of the bot's commands."""
    commands_list = (
        "**!set_channel [#channel]** - Set the channel for daily Golarion date updates. (Admin only)\n"
        "**!current_channel** - Display the channel currently set for daily updates.\n"
        "**!post_date** - Manually post the current Golarion date.\n"
        "**!next_holiday** - Display the next upcoming holiday and how many days away it is.\n"
        "**!set_year_offset [offset]** - Manually adjust the Golarion year offset. (Admin only)\n"
        "**!calendar_help** - Display this help message."
    )
    await ctx.send(f"Here are the commands you can use:\n{commands_list}")

# Ping command to check if the bot is responsive
@bot.command(name="ping")
@is_admin()
async def ping(ctx):
    """Ping the bot to check if it is responsive."""
    await ctx.send("Pong!")

# Database functions
def get_tracked_channels():
    """Fetch tracked channels from the database."""
    return session.query(TrackedChannel).all()

def save_channel(guild_id, channel_id):
    """Save the tracked channel to the database."""
    existing = session.query(TrackedChannel).filter_by(guild_id=guild_id).first()
    if existing:
        existing.channel_id = channel_id  # Update the channel ID
    else:
        new_channel = TrackedChannel(guild_id=guild_id, channel_id=channel_id)
        session.add(new_channel)
    session.commit()

# Run the bot
bot.run(TOKEN)
