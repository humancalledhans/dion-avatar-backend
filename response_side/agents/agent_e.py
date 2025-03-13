import requests
import urllib.parse


def get_agent_e_response(prompt, data, results_from_past_tools):

    try:

        print('agent edward-thorp')

        if not data:
            data = ""

        # print('results from past tools', results_from_past_tools)
        # print('type', type(results_from_past_tools))
        # input('verify input type first')

        # print("results_from_past_tool_calls 999",
        #       results_from_past_tool_calls[:100])

        # print("results_from_past_tool_calls", results_from_past_tools)

        full_prompt = (
            prompt + "\n" +
            "These are data obtained from official finance sources, please use them appropriately: " + data + "\n" +
            "These are results we've obtained from using past tools. Please use these appropriately:\n" +
            results_from_past_tools
        )

        print('check full prmopt bto', full_prompt[:500])

        # Encode the full string
        encoded_prompt = urllib.parse.quote(full_prompt)
        url = f"https://poppyai-api.vercel.app/api/conversation?api_key=gp_Energetic_Turtle_LZyL1NFyUhbsQdCWjFQq8T0xm7g2"

        payload = {
            "board_id": "autumn-cherry-IDdsX",
            "chat_id": "20-chatNode-small-leaf-RF9Rv",
            "prompt": full_prompt  # Send unencoded, full prompt
        }

        response = requests.post(url, json=payload)

        return response.json()

    except Exception as eett:
        print("excetion in agent b", eett)
        raise

    # encoded_prompt = urllib.parse.quote(
    #     prompt + "\n" + "These are data obtained from official finance sources, please use them appropriately. ", data)

    # url = f"https://poppyai-api.vercel.app/api/conversation?api_key=gp_Energetic_Turtle_LZyL1NFyUhbsQdCWjFQq8T0xm7g2&board_id=autumn-cherry-IDdsX&chat_id=20-chatNode-small-leaf-RF9Rv&prompt={encoded_prompt}"

    # response = requests.get(url)

    # return response.json()
