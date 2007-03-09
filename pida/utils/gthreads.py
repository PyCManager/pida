# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 The PIDA Project 

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import threading
import gobject

class AsyncTask(object):
    """
    AsyncTask is used to help you perform lengthy tasks without delaying
    the UI loop cycle, causing the app to look frozen. It is also assumed
    that each action that the async worker performs cancels the old one (if
    it's still working), thus there's no problem when the task takes too long.
    You can either extend this class or pass two callable objects through its
    constructor.
    
    The first on is the 'work_callback' this is where the lengthy
    operation must be performed. This object may return an object or a group
    of objects, these will be passed onto the second callback 'loop_callback'.
    You must be aware on how the argument passing is done. If you return an
    object that is not a tuple then it's passed directly to the loop callback.
    If you return `None` no arguments are supplied. If you return a tuple
    object then these will be the arguments sent to the loop callback.
    
    The loop callback is called inside Gtk+'s main loop and it's where you
    should stick code that affects the UI.
    """
    def __init__(self, work_callback=None, loop_callback=None):
        self.counter = 0
        
        if work_callback is not None:
            self.work_callback = work_callback
        if loop_callback is not None:
            self.loop_callback = loop_callback
    
    def start(self, *args, **kwargs):
        """
        Please note that start is not thread safe. It is assumed that this
        method is called inside gtk's main loop there for the lock is taken
        care there.
        """
        args = (self.counter,) + args
        threading.Thread(target=self._work_callback, args=args, kwargs=kwargs).start()
    
    def work_callback(self):
        pass
    
    def loop_callback(self):
        pass
    
    def _work_callback(self, counter, *args, **kwargs):
        ret = self.work_callback(*args, **kwargs)
        gobject.idle_add(self._loop_callback, (counter, ret))

    def _loop_callback(self, vargs):
        counter, ret = vargs
        if counter != self.counter:
            return
        
        if ret is None:
            ret = ()
        if not isinstance(ret, tuple):
            ret = (ret,)
            
        self.loop_callback(*ret)

class GeneratorTask(AsyncTask):
    """
    The diference between this task and AsyncTask is that the 'work_callback'
    returns a generator. For each value the generator yields the loop_callback
    is called inside Gtk+'s main loop.
    """
    def _work_callback(self, counter, *args, **kwargs):
        for ret in self.work_callback(*args, **kwargs):
            gobject.idle_add(self._loop_callback, (counter, ret))


def locked(lockname):
    '''
    Call this decorator with the name of the lock. The decorated method
    will be wrapped with an acquire()/lock().

    Example of usage::
        
        import threading
        
        class Foo(object):
            def __init__(self):
                self.lock = threading.Lock()
                
            @locked("lock")
            def meth1(self):
                self.critical_value = 1

            @locked("lock")
            def meth2(self):
                self.critical_value = 2
                return self.critical_value
    
    Both 'meth1' and 'meth2' will be wrapped with a 'lock.acquire()'
    and a 'lock.release()'.
    '''
def locked(lock_name):
    """This is a factory of decorators. The decorator
    wraps an acquire() and release() around the decorated
    method. The lock name is the name of the attribute
    containing the lock."""
    
    if not isinstance(lock_name, basestring):
        raise TypeError("'lock_name' must be a string")
    
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            lock = getattr(self, lock_name)
            lock.acquire()

            # Make sure an exception does not break
            # the lock
            try:
                ret = func(self, *args, **kwargs)
            except:
                lock.release()
                raise
            
            lock.release()
            return ret

        return wrapper

    return decorator

def gcall(func, *args, **kwargs):
    """
    Calls a function, with the given arguments inside Gtk's main loop.
    Example::
        gcall(lbl.set_text, "foo")

    If this call would be made in a thread there could be problems, using
    it inside Gtk's main loop makes it thread safe.
    """
    return gobject.idle_add(lambda: (func(*args, **kwargs) or False))

