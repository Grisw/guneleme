import os
import time
import subprocess


def main():
    os.system('sslocal -c /etc/ss.json &')
    time.sleep(3)
    while True:
        p = subprocess.Popen(['proxychains', 'qqbot', '-b', '/app/qqbot'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while p.poll() is None:
            s = p.stdout.readline().decode()
            print(s)
            if s == '&&RESTART@@':
                break
        p.kill()


if __name__ == '__main__':
    main()
