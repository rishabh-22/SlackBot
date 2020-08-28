import os
from slack import WebClient, RTMClient
from slack_util import slack_help, check_leaves


@RTMClient.run_on(event="message")
def listen_to_message(**payload):
    data = payload['data']
    web_client = payload['web_client']

    try:
        message = data['text']
        user = data['user']
        message_id = data['client_msg_id']
        time = data['event_ts']
        channel = data['channel']
        print([user, message, message_id, time, channel])
        deal_with_data({'user': user, 'message': message, 'message_id': message_id, 'channel': channel, 'time': time})
    except Exception as e:
        print(e)
        return None


def process_message(message, user, channel):
    # keywords = [help, apply, for, from, till, leave, reason, today, tomorrow, paid, casual, sick]
    words = message.split()

    if len(words) == 1 and words[0] == 'help':
        response = slack_help()
        web_client.chat_postMessage(
            channel=channel,
            text=response,
        )

    if len(words) == 1 and words[0] == 'check':
        response = check_leaves(user)
        web_client.chat_postMessage(
            channel=channel,
            text=response,
        )


def deal_with_data(data):
    if data:
        process_message(data['message'], data['user'], data['channel'])


if __name__ == '__main__':
    web_client = WebClient(os.environ.get('SLACK_TOKEN'))
    rtm_client = RTMClient(token=os.environ.get('SLACK_TOKEN'))
    rtm_client.start()
