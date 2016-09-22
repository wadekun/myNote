# _*_encoding: utf-8 _*_

import time, threading

'''
Python多线程

Python的标准库提供了两个模块：`thread`和`threading`，`thread`是低级模块。
`threading`是高级模块，对`thread`进行了封装。
大多数情况下，我们只需要使用`threading`模块。
'''

def loop():
    print 'thread %s is running...' % threading.current_thread().name
    n = 0
    while n < 5:
        n = n + 1
        print 'thread %s is running... %d' % (threading.current_thread().name, n)
        time.sleep(1)
    print 'thread %s is ended.' % threading.current_thread().name


def run_threads():
    # 使用 threading.Thread 来创建线程
    t1 = threading.Thread(target=loop, name='LoopThread1')
    t2 = threading.Thread(target=loop, name='LoopThread2')
    print 'thread %s is running...' % threading.current_thread().name

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print 'thread %s is ended.' % threading.current_thread().name


'''
LOCK：线程访问控制，保证了被锁代码块，同一时间点只能被一个线程访问
'''
# 全局变量
balance = 0
# 锁
lock = threading.Lock()

def change_balance(n):
    global balance # 获取全局变量
    balance = balance + n
    balance = balance - n

def multi_run_change(n):
    def run_change(n):
        for i in range(10000):
            lock.acquire() # 获取锁
            try:
                change_balance(n)
            finally:
                lock.release() # 释放锁

    t1 = threading.Thread(target=run_change, args=(n, ))
    t2 = threading.Thread(target=run_change, args=(n, ))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print 'balance now is %d' % balance


'''
Python 的多核利用问题

python的解释器在执行代码时，有一个内置的GIL锁(Global Interpreter Lock，全局解释器锁)，
任何python线程要执行前，都必须获取该全局锁，然后 每执行100条字节码，解释器就会释放GIL锁，让别的线程有机会执行。
所以，同一时刻，只会有一个python线程在执行。如果启用了多个线程，python程序只是在并发的执行，并没有并行。
这样，并不能充分利用多核的优势。

知乎上关于python 多线程，多核的讨论：https://www.zhihu.com/question/21219976
一篇很好的文章：http://zhuoqiang.me/python-thread-gil-and-ctypes.html

常见的解决方案有很多，比如可以创建CPU核数相等的进程来执行，发挥多核的优势。
当然，使用某种语言，当然是为了发挥该语言的优势，去解决相应的问题，如果要应对高并发，大吞吐量的话，
还是用 java/c/c++/go... 去吧。因为执行效率，本不是python追求的首位。
'''
def loop():
    while True:
        pass


def run_loop_thread():
    t1 = threading.Thread(target=loop, args=())
    t1.start()

if __name__ == '__main__':
    # run_threads()
    # multi_run_change(1)
    loop()
    run_loop_thread()
