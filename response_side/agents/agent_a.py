import requests
import urllib.parse


def get_agent_a_response(prompt, data):

    print('agent Cliff Asness')
    encoded_prompt = urllib.parse.quote(
        prompt + "\n" + "These are data obtained from official finance sources, please use them appropriately. ", data)

    url = f"https://poppyai-api.vercel.app/api/conversation?api_key=gp_Energetic_Turtle_LZyL1NFyUhbsQdCWjFQq8T0xm7g2&board_id=autumn-cherry-IDdsX&chat_id=18-chatNode-long-bush-qAE_T&prompt={encoded_prompt}"

    response = requests.get(url)

    return response.json()
