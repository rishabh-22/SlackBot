import logging
import os
import re
import pendulum
from slack import WebClient, RTMClient
from utils import slack_help, check_leaves, get_user_data, record_transaction


@RTMClient.run_on(event="message")
def listen_to_message(**payload):
    """
    this function is responsible for capturing the relevant data in case of a message event.
    :param payload:
    :return:
    """

    data = payload['data']

    try:
        message = data['text']
        user = data['user']
        message_id = data['client_msg_id']
        time = data['event_ts']
        channel = data['channel']
        process_data({'user': user, 'message': message, 'message_id': message_id, 'channel': channel, 'time': time})
    except Exception:
        return None


notification_channel = "#general"


def fetch_day(day, timezone):
    """
    this function is responsible for creating a date object based on the user input.
    :param day:
    :param timezone:
    :return:
    """

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
        logging.warning(e)
        return "Seems like there's some problem with the date input."


def send_message_to_chat(channel, response):
    """
    this function send a message to the specified channel.
    :param channel:
    :param response:
    :return:
    """

    web_client.chat_postMessage(
        channel=channel,
        text=response
    )


def process_data(data):
    """
    this method deals with the data entered by the user.
    :param data: dict
    :return: response to the user on chat.
    :keyword: [help, apply, for, from, till, leave, reason, yesterday, today, tomorrow, paid, casual, sick]
    """

    response = "Seems like there's some problem with the input."
    user_input = data['message'].split()

    try:

        if len(user_input) == 1 and user_input[0] == 'help':
            response = slack_help()
            return

        elif len(user_input) == 1 and user_input[0] == 'check':
            response = check_leaves(data['user'])
            return

        elif user_input[0] == 'apply':
            user_data = get_user_data(data['user'])
            leave_type = user_input[1]

            if 'for' in user_input:
                reason = ' '.join(user_input[6:])
                day = fetch_day(user_input[4], user_data['timezone'])
                if not reason:
                    response = "Please insert reason as well. (Followed by keyword `reason`)"
                    return

                update = record_transaction(user_data['email'], leave_type, day, day, reason,
                                            data['message_id'], data['time'])
                response = update['text']
                if update['status']:
                    send_message_to_chat(notification_channel, f"Hi Team, {user_data['name']} will be on leave "
                                                               f"{user_input[4]}. \nReason: {reason}")
                return

            elif 'from' and 'till' in user_input:
                reason = ' '.join(user_input[8:])
                # dealing with from day:
                start_day = fetch_day(user_input[4], user_data['timezone'])

                # dealing with till day:
                end_day = fetch_day(user_input[6], user_data['timezone'])
                delta = end_day - start_day
                if delta.days < 0 or delta.hours < 0:
                    response = "Please put in proper date. End date can't be prior to start date."
                    return
                if not reason:
                    response = "Please insert reason as well. (Followed by keyword `reason`)"
                    return

                update = record_transaction(user_data['email'], leave_type, start_day, end_day, reason,
                                            data['message_id'], data['time'])
                response = update['text']
                if update['status']:
                    send_message_to_chat(notification_channel, f"Hi Team, {user_data['name']} will be on leave from "
                                                     f"{start_day.to_date_string()} till {end_day.to_date_string()}. "
                                                     f"\nReason: {reason}")
                return

    except Exception as e:
        logging.error(e)

    finally:
        send_message_to_chat(data['channel'], response)


if __name__ == '__main__':
    web_client = WebClient(os.environ.get('SLACK_TOKEN'))
    rtm_client = RTMClient(token=os.environ.get('SLACK_TOKEN'))
    rtm_client.start()
