import os
import time


def main():
    os.system('sslocal -c /etc/ss.json &')
    time.sleep(3)
    while True:
        os.system('proxychains qqbot -b /app/qqbot')


if __name__ == '__main__':
    main()
