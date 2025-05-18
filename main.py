import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import asyncio
import random
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='?', intents=intents)
esperando_reaccion = {}

@bot.event
async def on_ready():
    for guild in bot.guilds:
        await guild.me.edit(nick=None)


# --- COMANDO: startteams con botones ---
@bot.command()
async def startteams(ctx):
    emoji = "🐒"
    max_players = 10
    host = ctx.author
    role_id = 1372747562528014378
    role_mention = f"<@&{role_id}>"
    allowed_mentions = discord.AllowedMentions(roles=True)

    await ctx.send(content=role_mention, allowed_mentions=allowed_mentions)

    embed = discord.Embed(
        title="🔥 React for 2vs2 | 3vs3 | 4vs4 | 5vs5",
        description=(
            f"React with {emoji} to join.\n"
            f"❗ **Max:** {max_players} participants.\n"
            f"✨ **Hosted by:** {host.mention}\n"
        ),
        color=discord.Color.red()
    )

    class TeamView(View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="✅ Start", style=discord.ButtonStyle.success)
        async def start(self, interaction: discord.Interaction, button: Button):
            if interaction.user != host:
                return await interaction.response.send_message("⚠️ Solo el host puede iniciar.", ephemeral=True)

            msg_id, emoji_char = esperando_reaccion.get(ctx.guild.id, (None, None))
            if not msg_id:
                return await interaction.response.send_message("❌ No hay sesión activa.", ephemeral=True)

            try:
                msg = await ctx.channel.fetch_message(msg_id)
                reaction = next(r for r in msg.reactions if str(r.emoji) == emoji_char)
                users = [u async for u in reaction.users() if not u.bot]
            except Exception as e:
                return await interaction.response.send_message(f"❌ Error al leer reacciones.\n`{type(e).__name__}: {e}`")

            total = len(users)
            if total < 2 or total % 2 != 0:
                return await interaction.response.send_message(f"⚠️ Se anotaron {total}. Necesitamos número par (2v2, 4v4, etc).")

            random.shuffle(users)
            mitad = total // 2
            team1 = users[:mitad]
            team2 = users[mitad:]

            result = (
                f"**🔴 Team 1:**\n" + "\n".join(u.mention for u in team1) + "\n\n" +
                f"**🔵 Team 2:**\n" + "\n".join(u.mention for u in team2)
            )

            embed_result = discord.Embed(
                title="🐒 Equipos Generados",
                description=result,
                color=discord.Color.orange()
            )
            embed_result.set_footer(text="¡Good Luck!")

            esperando_reaccion.pop(ctx.guild.id, None)
            await interaction.response.send_message(embed=embed_result)

        @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.danger)
        async def cancel(self, interaction: discord.Interaction, button: Button):
            if interaction.user != host:
                return await interaction.response.send_message("⚠️ Solo el host puede cancelar.", ephemeral=True)

            esperando_reaccion.pop(ctx.guild.id, None)
            await interaction.message.delete()
            await interaction.response.send_message("✅ Sesión cancelada.", ephemeral=False)

    msg = await ctx.send(embed=embed, view=TeamView())
    await msg.add_reaction(emoji)
    esperando_reaccion[ctx.guild.id] = (msg.id, emoji)

# --- COMANDO: /roast ---
class Roast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roast", description="Tira un roast suave para molestar a alguien.")
    async def roast(self, interaction: discord.Interaction, user: discord.Member):
        burns = [
            "fue tan malo que su propio team lo reportó en warmup.",
            "es el primer jugador en perder un 1v0.",
            "tiene más muertes que FPS.",
            "falla más que el WiFi en un cyber.",
            "tiene aim automático... pero descalibrado.",
            "pensaba que el tutorial era una partida ranked.",
            "no pierde partidas, las documenta para ciencia forense.",
            "hace que los bots parezcan tryhards.",
            "fue tan malo que el NPC le pidió perdón.",
            "hizo rage quit al que lo estaba espectando."
        ]
        chosen = random.choice(burns)
        await interaction.response.send_message(f" **{user.mention}** {chosen}")

# --- COMANDO: /excuse ---
class Excuse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="excuse", description="Genera una excusa graciosa para alguien que perdió.")
    async def excuse(self, interaction: discord.Interaction, user: discord.Member):
        excuses = [
            "se le apagó la PC justo cuando iba ganando.",
            "tenía 300 de ping y se le cayó el WiFi mientras se le escapaba el perro.",
            "no jugó en serio porque estaba comiendo una milanesa.",
            "jugó con los ojos cerrados para dar ventaja.",
            "pensaba que era práctica, no el partido real.",
            "le dolía la muñeca del LoL.",
            "estaba en modo ahorro de energía.",
            "le patearon el módem.",
            "estaba en otro universo mentalmente.",
            "fue saboteado por su gato.",
            "se le cayó el teclado.",
            "estaba en modo incógnito.",
            "se le cayó el Mouse.",
            "estaba en modo avión.",
            "estaba en modo silencio.",
            "estaba en modo do not disturb.",
            "estaba en modo pantalla dividida.",
            "estaba en modo pantalla completa.",
            "estaba en modo ventana.",
            "estaba en modo pantalla compartida.",
            "estaba en modo pantalla duplicada.",
            "se le cayó el monitor.",
            "se le desconecto",
            "se le desconecto el teclado",
            "se le desconecto el mouse",
            "se le desconecto el monitor",
            "se le desconecto el teclado y el mouse",
            
            
            
        ]
        chosen = random.choice(excuses)
        await interaction.response.send_message(f"🐒 **{user.mention}** perdió porque: *\"{chosen}\"*")

# --- COMANDO: /ping ---
class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check if the bot is alive.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong!")
        # --- COMANDO: /nickname ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setnickname(ctx, *, nickname: str):
    """Cambia el apodo del bot en este servidor."""
    try:
        if nickname.lower() == "none":
            await ctx.guild.me.edit(nick=None)
            await ctx.send("✅ Apodo eliminado, se usará el nombre global.")
        else:
            await ctx.guild.me.edit(nick=nickname)
            await ctx.send(f"✅ Nuevo apodo: `{nickname}`")
    except Exception as e:
        await ctx.send(f"❌ No se pudo cambiar el apodo: `{type(e).__name__}` - {e}")
        # --- COMANDO: ?whoami ---
@bot.command()
async def whoami(ctx):
    embed = discord.Embed(
        title="🤖 Bot Info",
        description=f"**Nombre:** `{bot.user.name}`\n**ID:** `{bot.user.id}`",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else discord.Embed.Empty)
    await ctx.send(embed=embed)

# --- on_ready ---
@bot.event
async def on_ready():
    await bot.add_cog(Ping(bot))
    await bot.add_cog(Excuse(bot))
    await bot.add_cog(Roast(bot))
    await bot.tree.sync()

    # 🔄 Elimina apodo en todos los servers
    for guild in bot.guilds:
        await guild.me.edit(nick=None)

    print("✅ Slash commands synced.")
    print(f"Bot online como: {bot.user} ({bot.user.id})")


# --- Mantener vivo y correr ---
keep_alive()
bot.run(os.getenv("TOKEN"))
