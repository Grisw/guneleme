import os
import time


def main():
    os.system('sslocal -c /etc/ss.json &')
    time.sleep(3)
    os.system('proxychains qqbot -b /app')


if __name__ == '__main__':
    main()
