import logging
import os
import socket
import multiprocessing
import subprocess


def pinger(job_q, results_q):
    """
    Пингуем все адреса подсети. Отвечающие хосты добавляем в список.
    """
    DEVNULL = open(os.devnull, 'w')
    while True:

        ip = job_q.get()

        if ip is None:
            break

        try:
            subprocess.check_call(['ping', '-c1', '-w1', ip],
                                  stdout=DEVNULL)
            results_q.put(ip)
            print(ip, os.getpid())
        except Exception:
            pass


def get_my_ip():
    """
    Получаем адрес текущего устройства
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def map_network(pool_size=255):
    """
    Функция получения списка адресов и имен хостов из текущей локальной подсети.
    """
    ip_list = list()

    # get my IP and compose a base like 192.168.1.xxx
    ip_parts = get_my_ip().split('.')
    base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'

    # prepare the jobs queue
    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()

    pool = [multiprocessing.Process(target=pinger,
                                    args=(jobs, results)) for i in range(pool_size)]

    print('start')
    for p in pool:
        p.start()

    # cue the ping processes
    print('jobs put')
    for i in range(1, 255):
        jobs.put(base_ip + '{0}'.format(i))

    print('none')
    for p in pool:
        jobs.put(None)

    print('join')
    for p in pool:
        p.join()

    # collect the results
    print('coll results')
    while not results.empty():
        ip = results.get()
        ip_list.append(ip)

    return ip_list


if __name__ == '__main__':
    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler('naslist.log')
    log = logging.getLogger('spam_application')
    log.addHandler(fh)

    print('Mapping...')
    ip_lst = map_network()
    print(ip_lst)
    for dev_ip in ip_lst:
        try:
            name, alias, addresslist = socket.gethostbyaddr(dev_ip)
            print(name, alias, addresslist)
        except Exception as e:
            print(dev_ip, e)
