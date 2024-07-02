import hashlib
import time
import uuid
import datetime
import config.common
import qrcode
import jwt


def api_response(code, msg, data={}, count=0):
    return {
        'code': code,
        'total': count,
        'msg': msg,
        'data': data
    }


def generate_pay_url(channel_id):
    cashier_client_host = config.common.CASHIER_CLIENT_HOST

    return f"{cashier_client_host}/?cid={channel_id}"


def generate_qrcode(channel_id):
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    pay_url = generate_pay_url(channel_id)
    qr.add_data(pay_url)

    qr.make(fit=True)
    img = qr.make_image()
    filename = f"{generate_unique_string(16)}.png"
    filepath = f"{config.common.QRCODE_ROOT_DIR}/{filename}"
    img.save(filepath)

    return filename


def generate_unique_string(length=32, prefix="", suffix=""):
    """
    Generate a unique string using UUID and timestamp.

    Args:
        length (int): The desired length of the unique string (default: 10).
        prefix (str): An optional prefix to add to the string.
        suffix (str): An optional suffix to add to the string.

    Returns:
        str: The generated unique string.
    """

    random_id = str(uuid.uuid4())[:length]
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_string = f"{prefix}{random_id}{timestamp}{suffix}"

    return unique_string


def generate_jwt(user_id, username, secret_key, algorithm="HS256"):
    payload = {
        'user_id': user_id,
        'username': username,
        'iat': datetime.datetime.utcnow().timestamp(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def md5(data):
    _md5 = hashlib.md5()
    _md5.update(data.encode())

    return _md5.hexdigest()


def generate_unique_order_number():
    order_no = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + str(time.time()).replace('.', '')[-7:])
    return order_no


import urllib.parse


def generate_query_string(data):
    # Sort the dictionary by keys in ascending order
    sorted_data = sorted(data.items(), key=lambda x: x[0])

    # Encode each key-value pair using urlencode
    encoded_params = [
        # urllib.parse.urlencode({key: value})
        f'{key}={value}'
        for key, value in sorted_data
    ]

    # Join the encoded pairs using '&' as the delimiter
    query_string = '&'.join(encoded_params)

    # # Remove the leading '&'
    # query_string = query_string[1:]

    return query_string


def get_pagination(current, page_size):
    current = int(current)
    page_size = int(page_size)

    start_index = (current - 1) * page_size
    end_index = start_index + page_size

    return start_index, end_index


if __name__ == '__main__':
    print(generate_unique_order_number())
    print(len(generate_unique_order_number()))
