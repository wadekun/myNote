#_*_ encoding:utf-8_*_

import os, time, random
from multiprocessing import Process, Pool, Queue

'''
Python中的多进程
'''


'''
windows平台并没有fork这个函数，so，os.fork() 这个底层调用在windows上并不能执行
'''
def run_fork(arg):
    print 'Process (%s) start...' % os.getpid()
    pid = os.fork()
    if pid == 0:
        print 'i\'m child process (%s) and my parent is %s' % (os.getpid(), os.getppid())
    else:
        print 'i\'m (%s) just created a child process (%s)' % (os.getpid(), pid)


'''
windows上可以使用multiprocessing.Process来模拟多进程
'''
def run_proc(arg):
    print 'run child process %s (%s)...' % (arg, os.getpid())

def create_sub_process():
    print 'parent process %s.' % os.getpid()
    p = Process(target=run_proc, args=('test', ))
    print 'sub process will start...'
    p.start() # 启动子进程
    p.join()  # 等待子进程结束
    print 'sub process end'


'''
启动大量子进程，可以使用进程池的方式批量创建子进程
'''
def long_time_task(name):
    print 'run task %s (%s)...' % (name, os.getpid())
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print 'Task %s runs %0.2f seconds.' % (name, (end - start))

'''
Pool 的默认大小是CPU的核心数
'''
def create_process_with_pool():
    print 'parent process %s.' % os.getpid()
    p = Pool()
    for i in range(9):
        p.apply_async(long_time_task, args=('sub_process:' + str(i), ))
    print 'waiting for all subprocesses done...'
    p.close() # 调用close() 方法，将不能向pool中提交子进程
    p.join()  # 等待所有子进程执行完毕， 必须在调用 close() 方法之后
    print 'all sub processes done.'


'''
进程间的通信
'''
def write(q):
    for value in ('A', 'B', 'C', ):
        print 'put %s to queue...' % value
        q.put(value)
        time.sleep(random.random())

def read(q):
    while True:
        try:
            value = q.get(timeout=5) # 设置超时时间为5秒
            print 'get %s from queue...' % value
        except Exception, e:
            print 'queue is empty... %s ' % e
            break


def processes_communication():
    q = Queue()
    p2 = Process(target=read, args=(q, ))
    p1 = Process(target=write, args=(q, ))
    print 'start write and read  sub process in parent %s' % os.getpid()
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print 'run end...'


if __name__ == '__main__':
    # create_sub_process()
    # create_process_with_pool()
    processes_communication()
