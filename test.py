import threading


class myThread(threading.Thread):
    def __init__(self,name,worker_func):  
        threading.Thread.__init__(self)
        self.worker_func=worker_func
        self.name = name
    
    def run(self):
        print("Starting " + self.name)
        self.worker_func()
        print("Exiting " + self.name)

def test():
	queueLock.acquire(timeout=10)




queueLock = threading.Lock()

workers = []

for i in range(2):
	t = myThread(str(i),test)
	t.run()
	workers.append(t)


# for t in workers:
#     t.join()