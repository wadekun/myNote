# _*_ encoding:utf-8 _*_

import threading

'''
ThreadLocal 一个Map结构，以当前线程为Key，保证变量只能当前线程可以访问.

最常见的应用场景比如 在数据库事务控制中，通过ThreadLocal存储当前线程的数据库连接，
保证每次取得都是同一个链接。
'''

# 创建全局ThreadLocal对象
local_user = threading.local()

def process_user():
    print 'hello, %s in %s' % (local_user.user, threading.current_thread().name)


def process_thread(name):
    # 绑定ThreadLocal的user
    local_user.user = name
    process_user()


t1 = threading.Thread(target=process_thread, args=('lili', ), name='Thread-A')
t2 = threading.Thread(target=process_thread, args=('lucy', ), name='Thread-B')

t1.start()
t2.start()
t1.join()
t2.join()
