import random
import string


def generatetoken():
    length = 30
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
