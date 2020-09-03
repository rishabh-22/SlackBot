import os
import re
import pendulum
from slack import WebClient, RTMClient
from utils import slack_help, check_leaves, get_user_data, record_transaction


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
        process_data({'user': user, 'message': message, 'message_id': message_id, 'channel': channel, 'time': time})
    except Exception as e:
        # print(e)
        return None


def fetch_day(day, timezone):
    try:
        if day == 'today':
            return pendulum.now(tz=timezone)
        elif day == 'tomorrow':
            return pendulum.tomorrow(tz=timezone)
        elif day == 'yesterday':
            return pendulum.yesterday(tz=timezone)
        elif re.match("^(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[0-2])/\d\d$", day):
            return pendulum.from_format(day, 'DD/MM/YY', tz=timezone)
    except Exception as e:
        print(e)
        return "Seems like there's some problem with the date input."


def send_message_to_chat(channel, response):
    web_client.chat_postMessage(
        channel=channel,
        text=response
    )


def process_data(data):
    # keywords = [help, apply, for, from, till, leave, reason, yesterday, today, tomorrow, paid, casual, sick]
    words = data['message'].split()

    if len(words) == 1 and words[0] == 'help':
        response = slack_help()
        send_message_to_chat(data['channel'], response)

    elif len(words) == 1 and words[0] == 'check':
        response = check_leaves(data['user'])
        send_message_to_chat(data['channel'], response)

    elif words[0] == 'apply':
        user_data = get_user_data(data['user'])
        leave_type = words[1]
        try:
            if 'for' in words:
                reason = ' '.join(words[6:])
                day = fetch_day(words[4], user_data['timezone'])
                # if not reason: response="please insert reason as well." return.
                response = record_transaction(user_data['email'], leave_type, day, day, reason,
                                              data['message_id'], data['time'])
                # if 'success' in response:
                #     send_message_to_chat("#general")
                send_message_to_chat(data['channel'], response)

            elif 'from' and 'till' in words:
                reason = ' '.join(words[8:])
                # dealing with from day:
                start_day = fetch_day(words[4], user_data['timezone'])

                # dealing with till day:
                end_day = fetch_day(words[6], user_data['timezone'])
                delta = end_day - start_day
                if delta.days < 0:
                    # return validation error
                    return send_message_to_chat(data['channel'], "Please put in proper date. "   # return from here
                                                                 "End date can't be prior to start date.")
                response = record_transaction(user_data['email'], leave_type, start_day, end_day, reason,
                                              data['message_id'], data['time'])
                send_message_to_chat(data['channel'], response)

                # apply reason checks.

        except Exception as e:
            print(e)
            send_message_to_chat(data['channel'], "Seems like there's some problem with the input.")
    else:
        send_message_to_chat(data['channel'], "Seems like there's some problem with the input.")


if __name__ == '__main__':
    web_client = WebClient(os.environ.get('SLACK_TOKEN'))
    rtm_client = RTMClient(token=os.environ.get('SLACK_TOKEN'))
    rtm_client.start()
