import os
from datetime import timedelta
from slack import WebClient
from pymongo import MongoClient


auth_client = WebClient(os.environ.get('AUTH_TOKEN'))
db_client = MongoClient(port=27017)
db = db_client.get_database('SlackBot')
leaves = db.get_collection('leaves')
transactions = db.get_collection('transactions')


def slack_help():
    """
    this function return the help text.
    :return:
    """
    response = "Hello! I am leaveBot, here to make it easy for you to apply for leaves.\n"\
        "I apply for leaves on your behalf. Here's the list off commands you can use with me:\n"\
        "`apply` : this command is used for applying for leaves, just enter one line in the specified format and " \
               "voila, your task is done.\n`check` : this command is used for checking your current leave balance." \
               "\nSince you're here, let me make you familiar with the formats, here are the `apply` command formats:" \
               "\n `apply` <type> `leave` `from` <DD/MM/YY> `till` <DD/MM/YY> `reason` <your reason>\n or " \
               "\n `apply` <type> `leave` `for` <today/tomorrow/yesterday> `reason` <your reason> " \
               "\nWhere as `check` is a standalone command. \nHope this helps. :D"
    return response


def get_user_data(user_id):
    """
    this function fetches the data of the user from slack API.
    :param user_id:
    :return:
    """

    response = auth_client.api_call("users.info", data={'user': user_id})
    if response:
        user_data = {
            'name': response['user']['real_name'],
            'email': response['user']['profile']['email'],
            'timezone': response['user']['tz']
        }
        return user_data
    return None


def check_leaves(user):
    """
    this function fetches the userdata from slack api and then uses
    that data to fetch the leave balance from the database
    :param user:
    :return:
    """
    # TODO: implement logging to check if api req failed or the database call.

    try:
        user_data = get_user_data(user)
        if not user_data:
            print("slack api failed.")

        leave_data = leaves.find_one({"_id": user_data['email']})
        if not leave_data:
            print("database call failed.")

        balance = leave_data['balance']
        if balance:
            response = ''
            for k, v in balance.items():
                response += k + ':' + str(v) + ' \n'
            return "Here's your leave balance:\n" + response

    except KeyError:
        return "Sorry, there seems to be some problem. I couldn't fetch your details."


def calculate_leaves(from_day, till_day):
    """
    this function calculates the total number of days for leaves excluding the weekends.
    :param from_day:
    :param till_day:
    :return:
    """

    day_generator = (from_day + timedelta(x + 1) for x in range((till_day - from_day).days))
    return 1 + sum(1 for day in day_generator if day.weekday() < 5)


def update_leaves(user_email, leave_type, total_leaves):
    """
    updates the leaves for the user in the database.
    :param user_email:
    :param leave_type:
    :param total_leaves:
    :return: acknowledgement
    """
    return leaves.update_one({"_id": user_email}, {"$inc": {f"balance.{leave_type}": int(-1*total_leaves)}}).\
        acknowledged


def record_transaction(user_email, leave_type, from_day, till_day, reason, message_id, event_time):
    """
    This function records the transaction and stores it into database and updates the leaves table accordingly.
    :param user_email:
    :param leave_type:
    :param from_day:
    :param till_day:
    :param reason:
    :param message_id:
    :param event_time:
    :return: dict of response with status and text.
    """
    response = {
        'status': False,
        'text': ""
    }
    try:
        total_leaves = calculate_leaves(from_day, till_day)
        data = leaves.find_one({"_id": user_email})

        if data['balance'][leave_type] < total_leaves:
            response['text'] = "Looks like you don't have enough of those leaves. " \
                               "You can check your leave balance by `check` command."
            return

        check = transactions.insert_one({
            "user_email": user_email,
            "leave_type": leave_type,
            "from": from_day,  # TODO: check the date format that goes into the database.
            "to": till_day,
            "total_leaves": total_leaves,
            "reason": reason,
            "message_id": message_id,
            "time": event_time
        }).acknowledged

        if check:
            if update_leaves(user_email, leave_type, total_leaves):
                response['status'] = True
                response['text'] = "Your leave(s) have been successfully updated with the system and " \
                                   "a notification has been sent to your colleagues."
                return
            else:
                response['text'] = "Sorry we're facing some issue at the backend, please try again later."
                return

    except KeyError:
        response['text'] = "Please look at the input value for leave type!"
        return
    except Exception as e:
        print(e)
        response['text'] = "There was some problem with the system, sorry for inconvenience, please try again later."
        return

    finally:
        return response

