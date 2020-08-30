import os
from slack import WebClient

auth_client = WebClient(os.environ.get('AUTH_TOKEN'))


leaves_db = {
    'rishabh.bh22@gmail.com': {
        'paid': 18,
        'casual': 3,
        'sick': 2
    },
    'devang.gaur.7@gmail.com': {
        'paid': 8,
        'casual': 2,
        'sick': 4
    },
}


def slack_help():
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
    data = get_user_data(user)
    balance = leaves_db.get(data.get('email'))
    if balance:
        response = ''
        for k, v in balance.items():
            response += k + ':' + str(v) + ' \n'
        return "Here's your leave balance:\n" + response
    else:
        return "Sorry, there seems to be some problem. I couldn't fetch your details."


# print(check_leaves('U014MHL52LB'))
