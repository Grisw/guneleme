import os
import time


def main():
    os.system('sslocal -c /etc/ss.json &')
    time.sleep(3)
    while True:
        p = os.popen('proxychains qqbot -b /app/qqbot', 'r', 1)
        while True:
            s = p.readline()
            if not s:
                break
            print(s)
            if s == '&&RESTART@@':
                break
        p.kill()


if __name__ == '__main__':
    main()
