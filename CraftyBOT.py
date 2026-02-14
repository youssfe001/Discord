import discord
from discord import app_commands
from discord.ext import commands
import datetime

# --- إعدادات السيرفر (ضع الـ IDs الخاصة بك هنا) ---
TOKEN = 'MTQ3MjA0NTY0ODAxNzYyNTE1Mg.GvsuKk.YTxPWMvcm5GW3AjfSa0reI1vbgyBxBHpqtlnaQ'
PC_CHANNEL_ID = 1472031752213233707    
MOBILE_CHANNEL_ID = 1472031348926582814
ADMIN_ROLE_ID = 1450957069938327813  # <--- ضع هنا ID رتبة الإدارة (Admin Role ID)

class CraftyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.moderation = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Crafty Online | تم ربط الإدارة عبر الـ ID: {ADMIN_ROLE_ID}")

bot = CraftyBot()

# --- دالة التحقق عبر الـ ID ---
def is_admin():
    async def predicate(interaction: discord.Interaction):
        # التحقق إذا كان لدى المستخدم رتبة تحمل نفس الـ ID المحدّد
        has_role = any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles)
        if has_role:
            return True
        await interaction.response.send_message("❌ نعتذر، هذا الأمر مخصص للإدارة فقط.", ephemeral=True)
        return False
    return app_commands.check(predicate)

# --- [نظام النشر] ---
@bot.tree.command(name="script", description="نشر سكربت جديد")
@app_commands.describe(platform="المنصة", name="الاسم", description="الوصف", image="الصورة", video="الفيديو")
@app_commands.choices(platform=[
    app_commands.Choice(name="💻 Craftland PC Edition", value="pc"),
    app_commands.Choice(name="📱 Craftland Mobile Edition", value="mobile")
])
async def script(interaction: discord.Interaction, platform: app_commands.Choice[str], name: str, description: str, image: discord.Attachment, video: discord.Attachment = None):
    target_id = PC_CHANNEL_ID if platform.value == "pc" else MOBILE_CHANNEL_ID
    color = 0x3498db if platform.value == "pc" else 0xe67e22
    channel = bot.get_channel(target_id)

    embed = discord.Embed(title=f"📜 {name}", description=f"\n{description}\n", color=color)
    embed.set_author(name=f"المبدع: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    embed.set_image(url=image.url)
    embed.set_footer(text="Crafty System • Craftland MEA")

    await interaction.response.defer(ephemeral=True)
    await channel.send(embed=embed)
    if video:
        video_file = await video.to_file()
        await channel.send(content=f"🎥 **فيديو استعراض السكربت:**", file=video_file)
    await interaction.followup.send(f"✅ تم النشر بنجاح!", ephemeral=True)

# --- [نظام الإدارة] ---

@bot.tree.command(name="ban", description="حظر عضو")
@is_admin()
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "غير محدد"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"✅ تم حظر {member.mention}")

@bot.tree.command(name="unban", description="فك حظر بالاسم")
@is_admin()
async def unban(interaction: discord.Interaction, name: str):
    banned_users = [entry async for entry in interaction.guild.bans()]
    for ban_entry in banned_users:
        if ban_entry.user.name.lower() == name.lower():
            await interaction.guild.unban(ban_entry.user)
            return await interaction.response.send_message(f"✅ تم فك حظر {ban_entry.user.name}")
    await interaction.response.send_message("❌ الاسم غير موجود.")

@bot.tree.command(name="kick", description="طرد عضو")
@is_admin()
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "غير محدد"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ تم طرد {member.mention}")

@bot.tree.command(name="mute", description="كتم عضو")
@is_admin()
@app_commands.choices(duration=[
    app_commands.Choice(name="دقيقة", value=60),
    app_commands.Choice(name="ساعة", value=3600),
    app_commands.Choice(name="يوم", value=86400)
])
async def mute(interaction: discord.Interaction, member: discord.Member, duration: app_commands.Choice[int]):
    await member.timeout(datetime.timedelta(seconds=duration.value))
    await interaction.response.send_message(f"🔇 تم كتم {member.mention} لمدة {duration.name}")

@bot.tree.command(name="unmute", description="فك كتم")
@is_admin()
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(f"🔊 تم فك كتم {member.mention}")

bot.run(TOKEN)