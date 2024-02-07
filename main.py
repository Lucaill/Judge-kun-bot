import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# SQLiteデータベースに接続
conn = sqlite3.connect('player_data.db')
c = conn.cursor()

# テーブルが存在しない場合は作成
c.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        udemae TEXT
    )
''')

# 変更を保存
conn.commit()

# デフォルトの!helpコマンドを削除
bot.remove_command('help')

@bot.command(name='register')
async def register(ctx, udemae, *name):
    # ユーザーのIDを取得
    user_id = ctx.author.id

    # ユーザーがすでに登録されているか確認
    c.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    existing_player = c.fetchone()

    if existing_player:
        # ユーザーがすでに登録されている場合は更新
        c.execute('UPDATE players SET name = ?, udemae = ? WHERE user_id = ?', (' '.join(name), udemae, user_id))
    else:
        # ユーザーが登録されていない場合は新規登録
        c.execute('INSERT INTO players (user_id, name, udemae) VALUES (?, ?, ?)', (user_id, ' '.join(name), udemae))

    # 変更を保存
    conn.commit()

    await ctx.send(f"{ctx.author.mention}, プレイヤー情報を登録しました！")

@bot.command(name='myinfo')
async def myinfo(ctx):
    # ユーザーのIDを取得
    user_id = ctx.author.id

    # ユーザーが登録されているか確認
    c.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    player_info = c.fetchone()

    if player_info:
        await ctx.send(f"{ctx.author.mention}, あなたのプレイヤー情報:\n名前: {player_info[2]}\nウデマエ: {player_info[3]}")
    else:
        await ctx.send(f"{ctx.author.mention}, あなたのプレイヤー情報はまだ登録されていません。")

#ウデマエのマッピング
udemae_cost_mapping = {
    "X2600～": 10,
    "X2550~2599": 9,
    "X2500~2549": 8,
    "X2450~2499": 7,
    "X2400~2449": 6,
    "X2350~2399": 5,
    "X2300~2349": 4,
    "X2200～2299": 3,
    "X~2199": 2,
    "S+": 1,
    "S以下": 0,
}

@bot.command(name='team')
async def team(ctx, *players):
    if len(players) != 8:
        await ctx.send("プレイヤーはちょうど8人指定してください。")
        return

    # プレイヤーデータを取得
    team_players = []

    for player_name in players:
        c.execute('SELECT * FROM players WHERE name = ?', (player_name,))
        player = c.fetchone()

        print(f"指定されたプレイヤー: {player_name}")
        print(f"取得したプレイヤーデータ: {player}")

        if player:
            team_players.append(player)
        else:
            await ctx.send(f"{player_name} は見つかりませんでした。")

    # プレイヤーをウデマエのコストでソート
    sorted_players = sorted(team_players, key=lambda x: udemae_cost_mapping.get(x[3], 0))

    # 2つのチームに分ける
    team1 = sorted_players[:4]
    team2 = sorted_players[4:]

    # チーム分けの結果を表示
    await ctx.send("チーム1:")
    for player in team1:
        await ctx.send(f"{player[2]} - {player[3]}")

    await ctx.send("\nチーム2:")
    for player in team2:
        await ctx.send(f"{player[2]} - {player[3]}")
    print("チーム分け完了")  # デバッグ用

@bot.command(name='bot_help')
async def help_command(ctx):
    # Embedを使ったヘルプメッセージ
    embed = discord.Embed(
        title="ヘルプコマンド",
        description="このBOTのコマンド一覧です。",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="`!register [udemae] [name]`",
        value="プレイヤー情報を登録します。",
        inline=False
    )
    embed.add_field(
        name="`!myinfo`",
        value="自分のプレイヤー情報を表示します。",
        inline=False
    )
    embed.add_field(
        name="`!team [player1] [player2] ...`",
        value="チーム分けを行います。",
        inline=False
    )
    embed.add_field(
        name="`!bot_help`",
        value="このヘルプを表示します。",
        inline=False
    )

    await ctx.send(embed=embed)

# ここにBOTトークンを入力
bot.run('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')

# データベース接続を閉じる
conn.close()



