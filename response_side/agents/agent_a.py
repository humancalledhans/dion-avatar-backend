import requests
import urllib.parse


def get_agent_a_response(prompt, data, results_from_past_tools):

    if not data:
        data = ""

    full_prompt = (
        prompt + "\n" +
        "These are data obtained from official finance sources, please use them appropriately: " + data + "\n" +
        "These are results we've obtained from using past tools. Please use these appropriately:\n" +
        results_from_past_tools
    )

    print('check full prmopt bto', full_prompt[:500])

    print('agent Cliff Asness')
    # Encode the full string
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://poppyai-api.vercel.app/api/conversation?api_key=gp_Energetic_Turtle_LZyL1NFyUhbsQdCWjFQq8T0xm7g2"

    payload = {
        "board_id": "autumn-cherry-IDdsX",
        "chat_id": "18-chatNode-long-bush-qAE_T",
        "prompt": full_prompt  # Send unencoded, full prompt
    }

    response = requests.post(url, json=payload)

    return response.json()
