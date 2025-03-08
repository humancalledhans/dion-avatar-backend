import requests
import urllib.parse


def get_agent_s_response(prompt):

    encoded_prompt = urllib.parse.quote(prompt)

    url = f"https://poppyai-api.vercel.app/api/conversation?api_key=gp_Energetic_Turtle_LZyL1NFyUhbsQdCWjFQq8T0xm7g2&board_id=autumn-cherry-IDdsX&chat_id=16-chatNode-purple-dream-kxxkw&prompt={encoded_prompt}"

    response = requests.get(url)

    return response.json()
