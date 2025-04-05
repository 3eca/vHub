import app as app
from socket import socket, AF_INET, SOCK_DGRAM
import utils.logs as logs
from os import path


LOGER = logs.get_logger(path.basename(__file__))

s = socket(AF_INET, SOCK_DGRAM)
s.connect(("1.1.1.1", 80))
laddr = s.getsockname()[0]
s.close()


if __name__ == '__main__':
    LOGER.info('vHub app started.')
    app.app.run(
        host=laddr,
        port=3000,
        debug=True
    )
