import requests
import urllib.parse


def get_general_response(prompt):

    print('agent Jim Simons')
    encoded_prompt = urllib.parse.quote(prompt)

    print('encoded prompt 22', encoded_prompt)

    url = f"https://poppyai-api.vercel.app/api/conversation?api_key=gp_Energetic_Turtle_LZyL1NFyUhbsQdCWjFQq8T0xm7g2&board_id=autumn-cherry-IDdsX&chat_id=24-chatNode-dawn-resonance-RN1Zs&prompt={encoded_prompt}"

    response = requests.get(url)

    print("CHECK OUT RESPONSE !!", response.json())

    try:
        return response.json()['ai_reply']
    except KeyError:
        return response.json()['text']
