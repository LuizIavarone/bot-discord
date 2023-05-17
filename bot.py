TOKEN = ''

import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

class ExemploView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.field_ponto_fechado = None

    @discord.ui.button(label="Abrir Ponto", style=discord.ButtonStyle.green,custom_id="abrir_ponto")
    async def meu_botao(self, button: discord.ui.Button, interaction: discord.Interaction):

        validador = 0
        nome_usuario = self.ctx.author.name
        horario_abertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nome_sala = f"ponto_{nome_usuario}"
        nome_sala_validar = str(nome_sala).lower()

        deleteMessage = await self.ctx.message.delete()

        channel = discord.utils.get(self.ctx.guild.text_channels, name=nome_sala)

        for text_channel in self.ctx.guild.text_channels:
            text_channel = str(text_channel).lower()
            if text_channel == nome_sala_validar:
                validador = 1
                break

        if validador > 0:
            await self.ctx.send(f"Seu ponto já está aberto, verifique a sala {nome_sala_validar}", delete_after = 10)
        else:
            categoria = "📱 Controle"
            category = discord.utils.get(self.ctx.guild.categories, name=categoria)
            overwrites = {
                self.ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                self.ctx.author: discord.PermissionOverwrite(read_messages=True)
            }
            self.nova_sala = await self.ctx.guild.create_text_channel(nome_sala,category=category,overwrites=overwrites)

            embed = discord.Embed(title="Ponto Aberto", color=discord.Color.green())
            embed.add_field(name="Usuário", value=nome_usuario, inline=False)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/779178302597890128/1107416590200344606/Departamento_de_policia_metropole.png?width=702&height=702")
            self.field_ponto_aberto =embed.add_field(name="Ponto Aberto", value=horario_abertura, inline=False)
            self.field_ponto_fechado = embed.add_field(name="Ponto Fechado", value="", inline=False)
            self.field_tempo_servico = embed.add_field(name="Tempo de Serviço", value="", inline=False)

            embed.set_footer(text=f"Clique em ❌ para fechar o ponto")

            message = await self.nova_sala.send(embed=embed)
            self.embed_abertura = message.embeds[0] 

            await message.add_reaction("❌")

            def check(reaction, user):
                return str(reaction.emoji) == "❌" and user == self.ctx.author and reaction.message.id == message.id

            try:
                reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=60.0, check=check)
                embed_dict = embed.to_dict()
                horario_fechamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pontoAberto = ""
                formato = "%Y-%m-%d %H:%M:%S"
                for field in embed_dict["fields"]:
                    if field['name'] == "Ponto Fechado":
                        field["value"] += str(horario_fechamento)
                    if field['name'] == "Ponto Aberto":
                        pontoAberto = field["value"]

                if pontoAberto:
                    pontoAberto = datetime.strptime(pontoAberto, formato)
                else:
                    pontoAberto = None

                horario_fechamento = datetime.strptime(horario_fechamento, formato)

                if horario_fechamento and pontoAberto:
                    tempoTrabalhado = horario_fechamento - pontoAberto
                    diferenca_horas = tempoTrabalhado.total_seconds() / 3600
                    diferenca_horas = round(diferenca_horas,2)
                    for field in embed_dict["fields"]:
                        if field['name'] == "Tempo de Serviço":
                            field["value"] += str(diferenca_horas)
                

                embed = discord.Embed.from_dict(embed_dict)
                pontoFechado = await message.edit(embed=embed)
                channel = reaction.message.channel

                if not channel.permissions_for(channel.guild.me).send_messages:
                    x = 1 + 1
                    return

                destino = discord.utils.get(channel.guild.text_channels, name="log-ponto")
                if not destino:
                    x = 1 + 1
                    return
                if not destino.permissions_for(channel.guild.me).send_messages:
                    x = 1 + 1
                    return
                
                await destino.send(embed=embed)
                x = 1 + 1

                if self.ctx.author.guild_permissions.manage_channels:
                    channel = discord.utils.get(self.ctx.guild.text_channels, name=nome_sala_validar)
                    if channel:
                        await channel.delete()
                    else:
                        x = 1 + 1
                else:
                    x = 1 + 1
            except TimeoutError:
                x = 1 + 1


@bot.event
async def on_ready():
    x = 1 + 1

@bot.command()
async def ponto(ctx):
    view = ExemploView(ctx)
    await ctx.send("Clique no botão abaixo para abrir seu ponto.",delete_after = 10,view=view)

bot.run(TOKEN)