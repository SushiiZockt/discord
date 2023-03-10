#_________________________________________________________________ START ___________________________________________________________________________#

import discord
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
import asyncio
import json
import cfg


bot=discord.Client(intents=discord.Intents.all())
tree=app_commands.CommandTree(bot)
guild=discord.Object(id=cfg.GUILD_ID)


@bot.event
async def on_ready():
    await tree.sync(guild=guild)
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Team-Impact | /help"))
    print(f"We have logged in as {bot.user}.")

#________________________________________________________________ /START/ __________________________________________________________________________#

#____________________________________________________________ Willkommennachricht _____________________________________________________________________#

    
@bot.event
async def on_member_join(member):
    guild: discord.Guild = bot.get_guild(cfg.GUILD_ID)
    willkommen_embed = discord.Embed(title="Member Join", description=f"{member.mention} ist dem Server beigetreten!", color=discord.Color.green())
    willkommen_embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
    await bot.get_channel(cfg.CHANNEL_LOGS).send(embed=willkommen_embed)

    await member.add_roles(guild.get_role(cfg.ROLE_MEMBER))
    await member.add_roles(guild.get_role(cfg.ROLE_ABOUT_ME))
    await member.add_roles(guild.get_role(cfg.ROLE_VALORANT_RANK))
    await member.add_roles(guild.get_role(cfg.ROLE_GAME))
    await member.add_roles(guild.get_role(cfg.ROLE_EXTRAS))
    await member.add_roles(guild.get_role(cfg.ROLE_LEVEL))

    with open('users.json', 'r') as f:
        users = json.load(f)

    await update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f)

@bot.event
async def on_member_remove(member):
    embed = discord.Embed(title="Member Leave", description=f"`{member.name}#{member.discriminator}` ist vom Server gegangen!", color=discord.Color.red())
    embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
    await bot.get_channel(cfg.CHANNEL_LOGS).send(embed=embed)

    
#___________________________________________________________ /Willkommennachricht/ ____________________________________________________________________#

#_________________________________________________________________ Commands ___________________________________________________________________________#

@tree.command(name="help", description="Dieser Command zeigt alle Funktionen von diesem Bot. (Alle Member)", guild=guild)
async def self(interaction: discord.Integration):
    embed = discord.Embed(title=f"Help Command", description=f"Hi! Ich bin ein Bot für **{interaction.guild.name}** \n\n", color=discord.Color.blue())
    embed.add_field(name="Commands für jeden", value="`/help` - Das hier! \n`/stats` - Infos zum Server \n`/report` - Um Spieler zu Reporten", inline=False)
    embed.add_field(name="Commands für Admins", value="`/clear` - Zum Nachrichten löschen \n `/news` -  \n `/scrim` - \n `/ticket` - ")
    embed.add_field(name="Auto Channels", value="Wenn du in den <#1072212570041229322> Channel gehst wird dir Automatisch ein Channel erstellt.", inline=False)
    embed.add_field(name="Wichtige Channel", value=f"<#962405332527775764> - Ticket öffnen \n<#977850270140755978> - Eigene Rollen\n<#962403791171354624> - Regeln", inline=False)
    embed.add_field(name="Fragen?", value="Bei Fragen schreibe <@571039644490268673> an \noder mach ein <#962405332527775764> Ticket auf")
    embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
    await interaction.response.send_message(embed=embed, ephemeral=True)

#------------------------------------------------------------------------------------------------------------------------------------------------------#

@tree.command(name="abmeldung",guild=guild, description="Dieser Command ist für das Valorant Team um sich abzumelden. (Valorant Team)")
@app_commands.describe(member="Wer möchte sich abmelden?", zeitraum="Für welchen Zeitraum möchtest du dich abmelden?", grund="Warum meldest du dich ab?")
async def abmeldung(ctx, member:discord.Member, zeitraum:str, grund:str):
    role1 = discord.utils.get(ctx.guild.roles, id=cfg.ROLE_VALORANT_SPIELER) 
    role2 = discord.utils.get(ctx.guild.roles, id=cfg.ROLE_SERVER_TEAM_MEMBER)
    role3 = discord.utils.get(ctx.guild.roles, id=cfg.ROLE_VALORANT_ERSATZSPIELER)
    if role1 in ctx.user.roles or role2 in ctx.user.roles or role3 in ctx.user.roles:
        embed = discord.Embed(title="Neue Abmeldung", color=discord.Color.blue())
        embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Zeitraum", value=zeitraum, inline=False)
        embed.add_field(name="Grund", value=grund, inline=False)
        message = await bot.get_channel(cfg.CHANNEL_VALORANT_TEAM_ABMELDUNG).send(embed=embed)
        await message.add_reaction("✅")
        await ctx.response.send_message("Done", ephemeral=True)
    else:
        await ctx.response.send_message("Du hast kein Rechte für diesen Command!", ephemeral=True)
        return

#------------------------------------------------------------------------------------------------------------------------------------------------------#

@tree.command(name="report", guild=guild, description="Mit diesem Command kannst du einen Spieler Melden. (Alle Member)")
@app_commands.describe(member = "Wenn möchtest du melden?", reason="Warum möchtest du diese Person melden?")
async def self(ctx, member: discord.Member, reason: str):
    if member == ctx.user:
        await ctx.response.send_message(embed = discord.Embed(title="`❌` | Error", description="Du kannst dich nicht selber Reporten", color=discord.Color.red()), ephemeral = True)
        return
    
    embed_staff = discord.Embed(title=f"Report System", color=discord.Color.red())
    embed_staff.add_field(name="Reportet:", value=member.mention, inline=False)
    embed_staff.add_field(name="Reporter:", value=ctx.user.mention, inline=False)
    embed_staff.add_field(name="Grund:", value=reason, inline=False)
    embed_staff.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)

    
    await bot.get_channel(cfg.CHANNEL_LOGS).send(embed=embed_staff)

    await ctx.response.send_message(embed=discord.Embed(title="Reportet", description=f"Du hast {member.mention} Erfolgreich Reportet \n\n**Grund: {reason}**", color=discord.Color.green()), ephemeral=True)

#------------------------------------------------------------------------------------------------------------------------------------------------------#

@tree.command(name="news", guild=guild, description="Das ist ein Command für das Server Team (Owner Only)")
@app_commands.describe(beschreibung="Was möchtest du dem Server mitteilen?")
async def news(ctx, beschreibung:str):
    role = discord.utils.get(ctx.guild.roles, id=cfg.ROLE_OWNER)
    if not role in ctx.user.roles:
        await ctx.response.send_message("Du hast keine Rechte dazu!", ephemeral = True)
        return    
    embed = discord.Embed(title="News", description=beschreibung, color=discord.Color.blue())
    embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)

    await bot.get_channel(cfg.CHANNEL_NEUIGKEITEN).send(embed=embed)
    

    await ctx.response.send_message(embed = discord.Embed(title="`✅` | Fertig", description="Die Nachricht wurde gesendet!"), ephemeral = True)

#------------------------------------------------------------------------------------------------------------------------------------------------------#

@tree.command(name="clear", guild=guild, description="Mit diesem Command kann man Nachrichten aus Channeln löschen. (Owner Only)")
@app_commands.describe(amount="Wieviele Nachrichten möchtest du löschen?")
async def clear(ctx, amount:int):
    role = discord.utils.get(ctx.guild.roles, id=cfg.ROLE_OWNER)
    if not role in ctx.user.roles:
        await ctx.response.send_message("Du hast keine Rechte dazu!", ephemeral = True)
        return
    if amount == None:
        await ctx.response.send_message(embed = discord.Embed(title="`❌` | Error", description=f"Du musst einen Anzahl an Nachrichten eingeben\n\n /clear [amount]", color=discord.Color.red()), ephemeral=True)
        return
    else:
        try:
            int(amount)
        except:
            await ctx.send("Bitte geben sie eine Zahl ein!", ephemeral= True)
        else:
            await ctx.response.send_message(embed = discord.Embed(title="`✅` | Clear", description=f"Die Nachrichten werden gerade gelöscht"), ephemeral=True)
            await ctx.channel.purge(limit = amount)

#------------------------------------------------------------------------------------------------------------------------------------------------------#

@tree.command(name="regeln", guild=guild, description="Mit diesem Command werden die Regeln des Servers geschickt. (Owner Only)")
async def regeln(ctx):
    role = discord.utils.get(ctx.guild.roles, id=cfg.ROLE_OWNER)
    if not role in ctx.user.roles:
        await ctx.response.send_message("Du hast keine Rechte dazu!", ephemeral = True)
        return

    button = Button(label="✅ Verfiy", style=discord.ButtonStyle.green, custom_id="verfiy_button")
    view = View()
    view.add_item(button)

    embed = discord.Embed(title="Regelwerk",color=discord.Color.blue())
    embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
    embed.add_field(name="**Regel 1**",value="Die Discord ToS (Terms of Service) stehen über dem Regelwerk und das Staff Team und sind immer folge zu leisten.",inline= False)
    embed.add_field(name="**Regel 2**",value="Beleidigungen, rassiste und sexistische Ausdrücke jeglicher Form sind Verboten.",inline= False)
    embed.add_field(name="**Regel 3**",value="Jugendgefährdende oder pornographische Inhalte haben hier nichts zu suchen.",inline= False)
    embed.add_field(name="**Regel 4**", value="Das verbreiten von Key-Loggern, IP-Loggern oder schädlichen Anwendungen ist verboten.", inline= False)
    embed.add_field(name="**Regel 5**", value="Jegliche andere illegale Inhalte und Aktivitäten sind ebenso nicht gestattet.", inline=False)
    embed.add_field(name="**Regel 6**", value="Werbung für fremde Projekte ist nur nach Absprache mit der Leitungsebene erlaubt.", inline= False)
    embed.add_field(name="**Regel 7**", value="Programme die zum ändern der Stimme vorgesehen sind und Programme um Sound/Geräusche abzuspielen sind niemals erlaubt", inline= False)
    embed.add_field(name="**Regel 8**", value="Echtgeldhandel jeglicher Form ist nicht erlaubt.", inline= False)
    embed.add_field(name="**Regel 9**", value="Dem Staff Team wird nicht wiedersprochen und ihren Aussagen ist stets folge zu leisten.", inline= False)
    embed.add_field(name="**Regel 10**", value="Das Staff Team darf sich jeder Zeit das Recht einbehalten Änderungen am Regelwerk vorzunehmen.", inline= False)
    embed.add_field(name="**Regel 11**", value="Ausnutzen von Fehlern und Lücken im Regelwerk sind nicht gestattet.", inline= False)
    await ctx.channel.send(embed=embed, view=view)
    await ctx.response.send_message("Done", ephemeral=True)

#------------------------------------------------------------------------------------------------------------------------------------------------------#

@tree.command(name="info", guild=guild, description="Mit diesem Command werden die Server Infos geschickt. (Owner Only)")
async def info(ctx):
    role = discord.utils.get(ctx.guild.roles, id=cfg.ROLE_OWNER)
    if not role in ctx.user.roles:
        await ctx.response.send_message("Du hast keine Rechte dazu!", ephemeral = True)
        return
    embed = discord.Embed(title="Server Infos", color=discord.Color.blue())
    embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon)
    embed.add_field(inline=False, name="**Über uns**", value="Hey, wir sind ein **Valorant Team**. <@571039644490268673> und  <@529702626066169878> haben das Team gegründet und unser Team gibt es seid dem 09.04.2022.")
    embed.add_field(inline=False, name="**Unser Einladungslink**", value="> ★ **https://discord.gg/dp4Bw3VDAX**")
    embed.add_field(inline=False, name="**Unsere Valorant Teams**", value=" <@&962397564655783967>\n\n **Manager:**\n> ★ <@571039644490268673>\n\n**Spieler:**\n> ★ <@571039644490268673>\n> ★ <@1064191803928088666>\n> ★ <@257948810507059200>\n> ★ \n> ★\n\n**Ersatzspieler:**\n> ★ <@570197015875682304>\n\n\n<@&1038085745602220102>\n\n**Manager:**\n> ★ <@339010978668871680>\n\n**Spieler:**\n> ★ <@339010978668871680>\n> ★ <@617639608166907904>\n> ★ <@667810090232840192>\n> ★ <@742098068534591508>\n> ★ <@968197400223154216>\n\n**Ersatzspieler:**\n> ★")
    await ctx.channel.send(embed=embed)
    await ctx.response.send_message("Done", ephemeral=True)

#________________________________________________________________ /Commands/ __________________________________________________________________________#

#________________________________________________________________ Ticket Tool _________________________________________________________________________#


@tree.command(name="ticket", description="Dieser Command ist für das Ticket Embed. (Owner Only)", guild=guild)
async def ticketmsg(ctx: discord.Interaction):
    role = discord.utils.get(ctx.guild.roles, id=cfg.ROLE_OWNER)
    if not role in ctx.user.roles:
        await ctx.response.send_message("Du hast keine Rechte dazu!", ephemeral = True)
        return
    embed = discord.Embed(title="Allgemeiner Support", description="Wenn du Hilfe brauchst dann mach ein Ticket auf. Das Team ist immer für dich da :)", color=discord.Color.blue())
    valorant_button = Button(label="📮 Valorant Team Bewerbung", style=discord.ButtonStyle.blurple, custom_id="valorant-bewerbung")
    staff_button = Button(label="📮 Staff Bewerbung", style=discord.ButtonStyle.blurple, custom_id="staff-bewerbung")
    support_button = Button(label="📮 Allgemeiner Support", style=discord.ButtonStyle.blurple, custom_id="ticket_button")
    embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
    view = View()
    view.add_item(valorant_button)
    view.add_item(staff_button)
    view.add_item(support_button)

    embed_staff = discord.Embed(title='Staff Bewerbung', description='**Um unserem Team beizutreten, musst du die folgenden Anforderungen erfüllen!**\n\n **Grundvorraussetzungen:** \n- min. 15 Jahre\n- Aktiv auf dem Discord \n\n\n<@&1028283804680458240>\n- Grundkenntnisse von Html/CSS\n- fortgeschrittene Kenntnisse von Python\n- Discord Server einrichten können\n\n\n <@&967722620650913852>\n- Mit Menschen umgehen können\n- gutes Mikrofon \n\n', color=discord.Color.blue())
    embed_valorant = discord.Embed(title='Valorant Team Bewerbung', description='**Um unserem Team beizutreten, musst du die folgenden Anforderungen erfüllen!**\n\n **Grundvorraussetzungen:** \n- min. 15 Jahre\n- Ingame Name zu IMP (aber erst nach der Probezeit)\n- Sozialverhalten sollte stimmen \n\n\n<@&962397564655783967>\n- Rank: Plat 1 - Dia 3\n\n\n <@&1038085745602220102>\n- Rank: Bronze 1 - Gold 3\n \n\n', color=discord.Color.blue())
    embed_staff.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
    embed_valorant.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
    await ctx.channel.send(embeds=[embed_valorant ,embed_staff, embed], view=view)
    await ctx.response.send_message("Done", ephemeral=True)
    return

class modal_valorant(Modal, title = "Valorant Team Bewerbung"):
    vorname = TextInput(label="Dein Vorname:", style=discord.TextStyle.long, placeholder="Name", required=True, max_length=100)
    about_us = TextInput(label="Erzähle etwas über dich:", style=discord.TextStyle.long, placeholder="Alter, Hobby, Onlinezeiten usw.", required=True, max_length=450)
    spiel_erfahrung = TextInput(label="Wieviel Spiel erfahrung hast du?:", style=discord.TextStyle.long, placeholder="Ich spiel schon seit..., Ich war in ... Valorant Teams", required=True, max_length=450)
    warum = TextInput(label="Warum sollten wir dich nehmen?:", style=discord.TextStyle.long, placeholder="Weil, ich...", required=True, max_length=450)
    tracker = TextInput(label="Dein Valorant Tracker:", style=discord.TextStyle.long, placeholder="Tracker Link", required=True, max_length=100)


    async def on_submit(self, interaction: discord.Integration):
        embed = discord.Embed(title="Valorant Spieler Bewerbung", color=discord.Color.blue())
        embed.add_field(name=self.vorname.label, value=self.vorname, inline=False)
        embed.add_field(name=self.about_us.label, value=self.about_us, inline=False)
        embed.add_field(name=self.spiel_erfahrung.label, value=self.spiel_erfahrung, inline=False)
        embed.add_field(name=self.warum.label, value=self.warum, inline= False)
        embed.add_field(name=self.tracker.label, value=self.tracker, inline= False)
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar)
        embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
        await bot.get_channel(cfg.CHANNEL_BEWERBUNGEN).send(embed=embed)
        await interaction.response.send_message("Done", ephemeral=True)

class modal_staff(Modal, title = "Staff Bewerbung"):
    vorname = TextInput(label="Dein Vorname:", style=discord.TextStyle.long, placeholder="Name", required=True, max_length=15)
    about_us = TextInput(label="Erzähle etwas über dich:", style=discord.TextStyle.long, placeholder="Alter, Hobby usw.", required=True, max_length=500)
    onlinezeiten = TextInput(label="Onlinezeiten:", style=discord.TextStyle.long, placeholder="Ungefähr", required=True, max_length=100)
    position = TextInput(label="Welche Position?:", style=discord.TextStyle.long, placeholder="Supporter oder Developer", required=True, max_length=100)
    warum = TextInput(label="Warum sollten wir dich nehmen?", style=discord.TextStyle.long, placeholder="Weil, ich...", required=True, max_length=500)

    async def on_submit(self, interaction: discord.Integration):
        embed = discord.Embed(title="Staff Bewerbung", color=discord.Color.blue())
        embed.add_field(name=self.vorname.label, value=self.vorname, inline=False)
        embed.add_field(name=self.about_us.label, value=self.about_us, inline=False)
        embed.add_field(name=self.onlinezeiten.label, value=self.onlinezeiten, inline=False)
        embed.add_field(name=self.position.label, value=self.position, inline=False)
        embed.add_field(name=self.warum.label, value=self.warum, inline= False)
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar)
        embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
        await bot.get_channel(cfg.CHANNEL_BEWERBUNGEN).send(embed=embed)
        await interaction.response.send_message("Done", ephemeral=True)



@bot.event
async def on_interaction(interaction: discord.Integration):
    if interaction.channel.id == cfg.CHANNEL_TICKET or interaction.channel.id == cfg.CHANNEL_TEST:
        if "ticket_button" in str(interaction.data):
            guild = bot.get_guild(cfg.GUILD_ID)
            for ticket in guild.channels:
                if str(interaction.user) in ticket.name:
                    embed = discord.Embed(title="Ticket wurde nicht erstellt!", description=f"Du kannst nur ein Ticket zur selben Zeit öffnen! \nHier ist dein bereits geöffnetes Ticket! {ticket.mention}", color=discord.Color.blue())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            category = bot.get_channel(cfg.CATEGORY_SUPPORT_TICKET)
            ticket_channel = await guild.create_text_channel(f'🎫〡{interaction.user}', category=category, topic=f"Ticket von {interaction.user}(ID: {interaction.user.id})")
            
            global ticket_name
            ticket_name= f'🎫〡{interaction.user}'

            #Permission Set
            await ticket_channel.set_permissions(interaction.guild.default_role, view_channel=False)
            await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages = True, add_reactions=False, embed_links=True,attach_files=True, read_message_history=True, external_emojis=True)
            

            embed = discord.Embed(title="Neues Ticket!", description=f"Willkommen im Ticket {interaction.user.mention}! \n **Wie können wir dir weiterhelfen?**", color=discord.Color.blue())
            button1 = Button(label="❌ Close", style=discord.ButtonStyle.red, custom_id="close_button")
            view = View()
            view.add_item(button1)
            await ticket_channel.send(embed=embed, view=view)

            embed = discord.Embed(title="Ticket geöffnet!", description=f"Dein Ticket wurde erstellt! {ticket_channel.mention}", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    if "close_button" in str(interaction.data):
        embed = discord.Embed(description="Ticket schließt sich in 3 Sekunden automatisch!", color=discord.Color.red())
        await interaction.channel.send(embed=embed)
        await asyncio.sleep(3)
        await interaction.channel.delete()

        embed2 = discord.Embed(title="Ticket Closed", description=f"{interaction.user.mention} hat das Ticket `{ticket_name}` geschlossen!", color=discord.Color.red())
        embed2.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
        await bot.get_channel(cfg.CHANNEL_LOGS).send(embed=embed2)
        
    if "verfiy_button" in str(interaction.data):

        embed = discord.Embed(title="✅", description="Du hast dich erfolgreich verifiziert und hast die Role <@&1070348307517419582> bekommen", color=discord.Color.green())
        embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
        role = discord.utils.get(interaction.guild.roles, id=cfg.ROLE_VERIFIZERT)
        if role in interaction.user.roles:
            embed = discord.Embed(title="❌ Fehler", description="Du bist bereits verifiziert", color=discord.Color.red())
            embed.set_footer(text="Team-Impact | Offical Discord", icon_url="https://cdn.discordapp.com/attachments/962476037311184916/1048209560516689970/Team-Impact_Logo2.0.png")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        member = interaction.user
        await member.add_roles(role)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    if "valorant-bewerbung" in str(interaction.data):
        await interaction.response.send_modal(modal_valorant())
        
    if "staff-bewerbung" in str(interaction.data):
        await interaction.response.send_modal(modal_staff())


        
        
#______________________________________________________________________ /Ticket Tool/ _________________________________________________________________#


#___________________________________________________________________ ON VOICE STATE UPDATE ____________________________________________________________#


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:
        #Staff Warteraum Join Nachricht
        if after.channel.id  == cfg.VOICE_CHANNEL_STAFF_WARTERAUM:
            channel = bot.get_channel(cfg.CHANNEL_LOGS)
            embed = discord.Embed(title="Channel Join", description=f"{member.mention} ist dem Staff Warteraum beigetreten.", color=discord.Color.blue())
            embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
            await channel.send('<@&1038089947174936607>', embed=embed)

        #Auto Channel
        if after.channel.id == cfg.VOICE_CHANNEL_AUTO:
            for guild in bot.guilds:
                maincategory = discord.utils.get(guild.categories, id=cfg.CATEGORY_AUTO_CHANNEL)
                channel2 = await guild.create_voice_channel(name=f'{member.name}', category=maincategory)

                await channel2.set_permissions(member, manage_channels = True)
                await member.move_to(channel2)

                def check(x, y, z):
                    return len(channel2.members) == 0
                await bot.wait_for('voice_state_update', check=check)
                await channel2.delete()




#__________________________________________________________________ /ON VOICE STATE UPDATE/ ___________________________________________________________#

#______________________________________________________________________ Self Roles ____________________________________________________________________#


@tree.command(name="selfroles", description="Dieser Command ist für die Self Roles Embeds. (Owner Only)", guild=guild)
async def selfroles(ctx: discord.Interaction):
    role = discord.utils.get(ctx.guild.roles, id=cfg.ROLE_OWNER)
    if not role in ctx.user.roles:
        await ctx.response.send_message("Du hast keine Rechte auf diesen Command!", ephemeral=True)
        return

    await ctx.response.send_message("Done", ephemeral=True)
    games_embed = discord.Embed(title="Welche Spiele spielst du?", color=discord.Color.blue(), 
                                description=f"\n> {cfg.EMOJI_1} `-` Valorant"f"\n> {cfg.EMOJI_2} `-` Minecraft"f"\n> {cfg.EMOJI_3} `-` Apex"f"\n> {cfg.EMOJI_4} `-` CS:GO"f"\n> {cfg.EMOJI_5} `-` Warzone")
    games_embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)

    rank_embed = discord.Embed(title="Welchen Rank hast du in Valorant?", color=discord.Color.blue(), description=
                                f"\n> {cfg.EMOJI_UNRANKED} `-` Unranked"
                                f"\n> {cfg.EMOJI_IRON} `-` Iron"
                                f"\n> {cfg.EMOJI_BRONZE} `-` Bronze"
                                f"\n> {cfg.EMOJI_SILVER} `-` Silver"
                                f"\n> {cfg.EMOJI_GOLD} `-` Gold"
                                f"\n> {cfg.EMOJI_PLAT} `-` Platinium"
                                f"\n> {cfg.EMOJI_DIA} `-` Diamond"
                                f"\n> {cfg.EMOJI_ASC} `-` Ascendant"
                                f"\n> {cfg.EMOJI_IMMO} `-` Immortal"
                                f"\n> {cfg.EMOJI_RADIANT} `-` Radiant")
    rank_embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)

    alter_embed = discord.Embed(title="Wie alt bist du?", color=discord.Color.blue(),
                                description=f"\n> {cfg.EMOJI_FSK12} `-` 12-15 y/o"
                                            f"\n> {cfg.EMOJI_FSK16} `-` 16-17 y/o"
                                            f"\n> {cfg.EMOJI_FSK18} `-` 18+ y/o")
    alter_embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
    
    geschlecht_embed = discord.Embed(title="Als was identifizierst du dich?", color=discord.Color.blue(), description=
                                    f"\n> {cfg.EMOJI_MÄNNLICH} `-` Junge"
                                    f"\n> {cfg.EMOJI_WEIBLICH} `-` Mädchen")
    geschlecht_embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
    

    game_message = await ctx.channel.send(embed=games_embed)
    rank_message = await ctx.channel.send(embed=rank_embed)
    alter_message = await ctx.channel.send(embed=alter_embed)
    geschlecht_message = await ctx.channel.send(embed=geschlecht_embed)

    game_reaction = [cfg.EMOJI_1, cfg.EMOJI_2, cfg.EMOJI_3, cfg.EMOJI_4, cfg.EMOJI_5]
    rank_reaction = [cfg.EMOJI_UNRANKED, cfg.EMOJI_IRON, cfg.EMOJI_BRONZE, cfg.EMOJI_SILVER, cfg.EMOJI_GOLD, cfg.EMOJI_PLAT, cfg.EMOJI_DIA, cfg.EMOJI_ASC, cfg.EMOJI_IMMO, cfg.EMOJI_RADIANT]
    alter_reaction = [cfg.EMOJI_FSK12, cfg.EMOJI_FSK16, cfg.EMOJI_FSK18]
    geschlecht_reaction = [cfg.EMOJI_MÄNNLICH, cfg.EMOJI_WEIBLICH]


    for emoji in game_reaction:
        await game_message.add_reaction(emoji)
    for emoji in rank_reaction:
        await rank_message.add_reaction(emoji)
    for emoji in alter_reaction:
        await alter_message.add_reaction(emoji)
    for emoji in geschlecht_reaction:
        await geschlecht_message.add_reaction(emoji)


@bot.event
async def on_raw_reaction_add(payload):
    guild: discord.Guild = bot.get_guild(cfg.GUILD_ID)
    member = payload.member
    if payload.message_id == cfg.MSG_GAME:
        if payload.emoji.name == '1️⃣':
            await member.add_roles(guild.get_role(cfg.ROLE_VALORANT))
        if payload.emoji.name == '2️⃣':
            await member.add_roles(guild.get_role(cfg.ROLE_MINECRAFT))
        if payload.emoji.name == '3️⃣':
            await member.add_roles(guild.get_role(cfg.ROLE_APEX))
        if payload.emoji.name == '4️⃣':
            await member.add_roles(guild.get_role(cfg.ROLE_CSGO))
        if payload.emoji.name == '5️⃣':
            await member.add_roles(guild.get_role(cfg.ROLE_WARZONE))

    if payload.message_id == cfg.MSG_RANK:
        if payload.emoji.name == 'valorant_unranked':
            await member.add_roles(guild.get_role(cfg.ROLE_UNRANKED))
        if payload.emoji.name == 'valorant_iron':
            await member.add_roles(guild.get_role(cfg.ROLE_IRON))
        if payload.emoji.name == 'valorant_bronze':
            await member.add_roles(guild.get_role(cfg.ROLE_BRONZE))
        if payload.emoji.name == 'valorant_silver':
            await member.add_roles(guild.get_role(cfg.ROLE_SILVER))
        if payload.emoji.name == 'valorant_gold':
            await member.add_roles(guild.get_role(cfg.ROLE_GOLD))
        if payload.emoji.name == 'valorant_platinium':
            await member.add_roles(guild.get_role(cfg.ROLE_PLAT))
        if payload.emoji.name == 'valorant_diamond':
            await member.add_roles(guild.get_role(cfg.ROLE_DIA))
        if payload.emoji.name == 'valorant_ascendant':
            await member.add_roles(guild.get_role(cfg.ROLE_ASC))
        if payload.emoji.name == 'valorant_immortal':
            await member.add_roles(guild.get_role(cfg.ROLE_IMMO))
        if payload.emoji.name == 'valorant_radiant':
            await member.add_roles(guild.get_role(cfg.ROLE_RADIANT))

    if payload.message_id == cfg.MSG_ALTER:
        if payload.emoji.name == 'FSK_12':
            await member.add_roles(guild.get_role(cfg.ROLE_FSK12))
        if payload.emoji.name == 'FSK_16':
            await member.add_roles(guild.get_role(cfg.ROLE_FSK16))
        if payload.emoji.name == 'FSK_18':
            await member.add_roles(guild.get_role(cfg.ROLE_FSK18))

    if payload.message_id == cfg.MSG_GESCHLECHT:
        if payload.emoji.name == 'male':
            await member.add_roles(guild.get_role(cfg.ROLE_MÄNNLICH))
        if payload.emoji.name == 'female':
            await member.add_roles(guild.get_role(cfg.ROLE_WEIBLICH))

@bot.event
async def on_raw_reaction_remove(payload):
    guild: discord.Guild = bot.get_guild(cfg.GUILD_ID)
    member = guild.get_member(payload.user_id)
    if payload.message_id == cfg.MSG_GAME:
        if payload.emoji.name == '1️⃣':
            await member.remove_roles(guild.get_role(cfg.ROLE_VALORANT))
        if payload.emoji.name == '2️⃣':
            await member.remove_roles(guild.get_role(cfg.ROLE_MINECRAFT))
        if payload.emoji.name == '3️⃣':
            await member.remove_roles(guild.get_role(cfg.ROLE_APEX))
        if payload.emoji.name == '4️⃣':
            await member.remove_roles(guild.get_role(cfg.ROLE_CSGO))
        if payload.emoji.name == '5️⃣':
            await member.remove_roles(guild.get_role(cfg.ROLE_WARZONE))

    if payload.message_id == cfg.MSG_RANK:
        if payload.emoji.name == 'valorant_unranked':
            await member.remove_roles(guild.get_role(cfg.ROLE_UNRANKED))
        if payload.emoji.name == 'valorant_iron':
            await member.remove_roles(guild.get_role(cfg.ROLE_IRON))
        if payload.emoji.name == 'valorant_bronze':
            await member.remove_roles(guild.get_role(cfg.ROLE_BRONZE))
        if payload.emoji.name == 'valorant_silver':
            await member.remove_roles(guild.get_role(cfg.ROLE_SILVER))
        if payload.emoji.name == 'valorant_gold':
            await member.remove_roles(guild.get_role(cfg.ROLE_GOLD))
        if payload.emoji.name == 'valorant_platinium':
            await member.remove_roles(guild.get_role(cfg.ROLE_PLAT))
        if payload.emoji.name == 'valorant_diamond':
            await member.remove_roles(guild.get_role(cfg.ROLE_DIA))
        if payload.emoji.name == 'valorant_ascendant':
            await member.remove_roles(guild.get_role(cfg.ROLE_ASC))
        if payload.emoji.name == 'valorant_immortal':
            await member.remove_roles(guild.get_role(cfg.ROLE_IMMO))
        if payload.emoji.name == 'valorant_radiant':
            await member.remove_roles(guild.get_role(cfg.ROLE_RADIANT))

    if payload.message_id == cfg.MSG_ALTER:
        if payload.emoji.name == 'FSK_12':
            await member.remove_roles(guild.get_role(cfg.ROLE_FSK12))
        if payload.emoji.name == 'FSK_16':
            await member.remove_roles(guild.get_role(cfg.ROLE_FSK16))
        if payload.emoji.name == 'FSK_18':
            await member.remove_roles(guild.get_role(cfg.ROLE_FSK18))

    if payload.message_id == cfg.MSG_GESCHLECHT:
        if payload.emoji.name == 'male':
            await member.remove_roles(guild.get_role(cfg.ROLE_MÄNNLICH))
        if payload.emoji.name == 'female':
            await member.remove_roles(guild.get_role(cfg.ROLE_WEIBLICH))

#_______________________________________________________________ /Self Roles/ _________________________________________________________________________#


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    with open('levels.json', 'r') as f:
        users = json.load(f)


    await update_data(users, message.author)
    await add_exp(users, message.author, 5)
    await level_up(users, message.author)

    with open('levels.json', 'w') as f:
        json.dump(users, f)
        
async def update_data(users, member: discord.Member):
    if member.bot:
        return
    if not str(member.id) in users:
        users[str(member.id)] = {}
        users[str(member.id)]['exp'] = 0
        users[str(member.id)]['level'] = 1


async def add_exp(users, member: discord.Member, exp):
    if member.bot:
        return
    users[str(member.id)]['exp'] += exp

async def level_up(users, member: discord.Member):
    guild: discord.Guild = bot.get_guild(cfg.GUILD_ID)
    if member.bot:
        return
    exp = users[str(member.id)]['exp']
    lvl_start = users[str(member.id)]['level']
    lvl_end = int(exp ** (1/4))



    if lvl_start < lvl_end: 
        await bot.get_channel(cfg.CHANNEL_LEVEL).send(f'{member.mention} ist jetzt Level {lvl_end}. GG!')
        users[str(member.id)]['level'] = lvl_end
    
    if lvl_start >= 1:
        await member.add_roles(guild.get_role(cfg.ROLE_LEVEL_1))
        if lvl_start >= 5:
            await member.remove_roles(guild.get_role(cfg.ROLE_LEVEL_1))
            await member.add_roles(guild.get_role(cfg.ROLE_LEVEL_5))
            if lvl_start >= 10:
                await member.remove_roles(guild.get_role(cfg.ROLE_LEVEL_5))
                await member.add_roles(guild.get_role(cfg.ROLE_LEVEL_10))
                if lvl_start >= 15:
                    await member.remove_roles(guild.get_role(cfg.ROLE_LEVEL_10))
                    await member.add_roles(guild.get_role(cfg.ROLE_LEVEL_15))
                    if lvl_start >= 20:
                        await member.remove_roles(guild.get_role(cfg.ROLE_LEVEL_15))
                        await member.add_roles(guild.get_role(cfg.ROLE_LEVEL_20))
                        if lvl_start >= 30:
                            await member.remove_roles(guild.get_role(cfg.ROLE_LEVEL_20))
                            await member.add_roles(guild.get_role(cfg.ROLE_LEVEL_30))
                            if lvl_start >= 40:
                                await member.remove_roles(guild.get_role(cfg.ROLE_LEVEL_30))
                                await member.add_roles(guild.get_role(cfg.ROLE_LEVEL_40))
                                if lvl_start >= 50:
                                    await member.remove_roles(guild.get_role(cfg.ROLE_LEVEL_40))
                                    await member.add_roles(guild.get_role(cfg.ROLE_LEVEL_50))
    
@tree.command(name="level", guild=guild)
async def level(ctx: discord.Interaction,*, member:discord.Member):
    
    with open('levels.json', 'r') as f:
        users = json.load(f)

    if not str(member.id) in users:
        embed = discord.Embed(title="❌ Error", description="Dieser Member hat noch kein Level!", color=discord.Color.red())
        embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(title="Level System", color=discord.Color.blue())
    embed.set_author(name=member.name, icon_url=member.avatar)
    embed.set_footer(text=cfg.server_name, icon_url=cfg.server_icon_url)
    embed.add_field(name="Level:", value=users[str(member.id)]['level'])
    embed.add_field(name="Exp:", value=users[str(member.id)]['exp'])
    await ctx.response.send_message(embed=embed, ephemeral=True)








#__________________________________________________________________ TOKEN _____________________________________________________________________________#

bot.run(cfg.TOKEN)