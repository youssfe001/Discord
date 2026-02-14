import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

# ================= CONFIG =================
TOKEN = "MTQ3MjA0NTY0ODAxNzYyNTE1Mg.G-q_PC.08UJOlsxeGdROiUMQ9W45cEV2XJy_K4SPQrWuM"

PC_CHANNEL_ID = 1472031752213233707
MOBILE_CHANNEL_ID = 1472031348926582814
ADMIN_LOG_CHANNEL_ID = 1472231359203246284
ADMIN_ROLE_ID = 1450957069938327813
# ==========================================

# ===== COLORS =====
PC_COLOR = 0x3498db
MOBILE_COLOR = 0xe67e22
REVIEW_COLOR = 0xf1c40f


# ================= BOT =================
class Crafty(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash commands synced.")

    async def on_ready(self):
        print(f"✅ Logged in as {self.user}")


bot = Crafty()


# ================= ADMIN CHECK =================
def is_admin(member: discord.Member):
    role = member.guild.get_role(ADMIN_ROLE_ID)
    return role in member.roles if role else False


# ================= REVIEW VIEW =================
class ReviewView(discord.ui.View):
    def __init__(self, submission):
        super().__init__(timeout=None)
        self.submission = submission

    @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        channel_id = PC_CHANNEL_ID if self.submission["platform"] == "PC Edition" else MOBILE_CHANNEL_ID
        target_channel = interaction.guild.get_channel(channel_id)

        if not target_channel:
            await interaction.response.send_message("❌ Public channel not found.", ephemeral=True)
            return

        color = PC_COLOR if self.submission["platform"] == "PC Edition" else MOBILE_COLOR

        embed = discord.Embed(
            title=self.submission["name"],
            description=f"```{self.submission['description']}```",
            color=color,
            timestamp=datetime.utcnow()
        )

        embed.set_author(
            name=self.submission["author"].name,
            icon_url=self.submission["author"].display_avatar.url
        )

        embed.set_footer(text=f"Crafty • {self.submission['platform']}")

        attachments = self.submission["attachments"]

        if attachments:
            embed.set_image(url=attachments[0])

        await target_channel.send(embed=embed)

        if len(attachments) > 1:
            for file_url in attachments[1:]:
                await target_channel.send(file_url)

        await interaction.message.delete()
        await interaction.response.send_message("✅ Approved & Published.", ephemeral=True)

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        try:
            await self.submission["author"].send(
                f"❌ Your script **{self.submission['name']}** was rejected."
            )
        except:
            pass

        await interaction.message.delete()
        await interaction.response.send_message("❌ Script Rejected.", ephemeral=True)


# ================= MODAL =================
class ScriptModal(discord.ui.Modal, title="Submit Your Script"):

    name = discord.ui.TextInput(
        label="Script Title",
        max_length=100
    )

    description = discord.ui.TextInput(
        label="Script Description",
        style=discord.TextStyle.long,
        max_length=4000
    )

    def __init__(self, interaction, platform, attachments):
        super().__init__()
        self.interaction = interaction
        self.platform = platform
        self.attachments = attachments

    async def on_submit(self, interaction: discord.Interaction):

        admin_channel = interaction.guild.get_channel(ADMIN_LOG_CHANNEL_ID)

        if not admin_channel:
            await interaction.response.send_message(
                "❌ Admin channel not found. Check ADMIN_LOG_CHANNEL_ID.",
                ephemeral=True
            )
            return

        submission = {
            "name": self.name.value,
            "description": self.description.value,
            "platform": self.platform,
            "attachments": self.attachments,
            "author": interaction.user
        }

        embed = discord.Embed(
            title="📩 New Script Submission (Pending)",
            color=REVIEW_COLOR,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="Platform", value=self.platform, inline=True)
        embed.add_field(name="Title", value=self.name.value, inline=True)
        embed.add_field(name="Author", value=interaction.user.mention, inline=False)
        embed.add_field(name="Description", value=f"```{self.description.value}```", inline=False)

        view = ReviewView(submission)

        await admin_channel.send(embed=embed, view=view)

        await interaction.response.send_message(
            "✅ Your script has been submitted for review.",
            ephemeral=True
        )


# ================= SCRIPT COMMAND =================
@bot.tree.command(name="script", description="Submit a script")
@app_commands.describe(
    platform="Choose platform",
    attachment1="Optional file",
    attachment2="Optional file",
    attachment3="Optional file"
)
@app_commands.choices(platform=[
    app_commands.Choice(name="PC Edition", value="PC Edition"),
    app_commands.Choice(name="Mobile Edition", value="Mobile Edition")
])
async def script(
    interaction: discord.Interaction,
    platform: app_commands.Choice[str],
    attachment1: discord.Attachment = None,
    attachment2: discord.Attachment = None,
    attachment3: discord.Attachment = None
):

    attachments = [a.url for a in (attachment1, attachment2, attachment3) if a]

    modal = ScriptModal(interaction, platform.value, attachments)

    await interaction.response.send_modal(modal)


# ================= ADMIN COMMANDS =================
@bot.tree.command(name="clear", description="Clear messages")
async def clear(interaction: discord.Interaction, amount: int):

    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)


@bot.tree.command(name="kick", description="Kick member")
async def kick(interaction: discord.Interaction, member: discord.Member):

    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await member.kick()
    await interaction.response.send_message(f"👢 {member.mention} kicked.")


@bot.tree.command(name="ban", description="Ban member")
async def ban(interaction: discord.Interaction, member: discord.Member):

    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await member.ban()
    await interaction.response.send_message(f"🔨 {member.mention} banned.")


@bot.tree.command(name="mute", description="Timeout member")
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):

    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await member.timeout(duration)

    await interaction.response.send_message(
        f"🔇 {member.mention} muted for {minutes} minutes."
    )


# ================= RUN =================
bot.run(TOKEN)
