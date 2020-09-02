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


def process_data(data):
    # keywords = [help, apply, for, from, till, leave, reason, yesterday, today, tomorrow, paid, casual, sick]
    words = data['message'].split()

    if len(words) == 1 and words[0] == 'help':
        response = slack_help()
        web_client.chat_postMessage(
            channel=data['channel'],
            text=response,
        )

    if len(words) == 1 and words[0] == 'check':
        response = check_leaves(data['user'])
        web_client.chat_postMessage(
            channel=data['channel'],
            text=response,
        )

    if words[0] == 'apply':
        user_data = get_user_data(data['user'])
        leave_type = words[1]
        try:
            if 'for' in words:
                reason = ' '.join(words[6:])
                day = fetch_day(words[4], user_data['timezone'])
                response = record_transaction(user_data['email'], leave_type, day, day, reason,
                                              data['message_id'], data['time'])
                web_client.chat_postMessage(
                    channel=data['channel'],
                    text=response
                )

            elif 'from' and 'till' in words:
                reason = ' '.join(words[8:])
                # dealing with from day:
                start_day = fetch_day(words[4], user_data['timezone'])

                # dealing with till day:
                end_day = fetch_day(words[6], user_data['timezone'])
                delta = end_day - start_day
                if delta.days < 0:
                    # return validation error
                    web_client.chat_postMessage(
                        channel=data['channel'],
                        text="Please put in proper date. Start date can't be prior to end date."
                    )
                response = record_transaction(user_data['email'], leave_type, start_day, end_day, reason,
                                              data['message_id'], data['time'])
                web_client.chat_postMessage(
                    channel=data['channel'],
                    text=response
                )

        except Exception as e:
            print(e)
            web_client.chat_postMessage(
                channel=data['channel'],
                text="Seems like there's some problem with the input."
            )
    else:
        web_client.chat_postMessage(
            channel=data['channel'],
            text="Seems like there's some problem with the input."
        )


# def deal_with_data(data):
#     if data:
#         process_message(data['message'], data['user'], data['channel'])


if __name__ == '__main__':
    web_client = WebClient(os.environ.get('SLACK_TOKEN'))
    rtm_client = RTMClient(token=os.environ.get('SLACK_TOKEN'))
    rtm_client.start()
