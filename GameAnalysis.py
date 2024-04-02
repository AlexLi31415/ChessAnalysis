import asyncio

from chessdotcom.aio import get_player_profile

def get_player_games(user):

    player = get_player_profile(user)

    async def gather_cors(player):
        return await asyncio.gather(player)

    responses = asyncio.run(gather_cors(player))
    
    return responses