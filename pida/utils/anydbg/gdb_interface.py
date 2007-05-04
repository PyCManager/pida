# -*- coding: utf-8 -*- 

# Copyright (c) 2007 The PIDA Project

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

import os
import re

# --- AnyDbg debugger classes

class AnyDbg_Debugger:
    def __init__(self, executable, parameters, service, param):
        self._executable = executable
        self._parameters = parameters
        self.svc = service
        self._dbg_param = param

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def step_in(self):
        raise NotImplementedError

    def step_over(self):
        raise NotImplementedError

    def toggle_breakpoint(self, file, line):
        raise NotImplementedError

class AnyDbg_gdb(AnyDbg_Debugger):
    _console = None
    _breakpoints = []

    _parser_patterns = {
        # line: Restarting <EXEC> with arguments: <ARGS>
        'Restarting (.*) with arguments:(.*)' : 
            lambda self, m: self.svc.emit('start_debugging', 
                                                    executable=m.group(1), 
                                                    arguments=m.group(2)),
        # line: *** Blank or comment
        '\*\*\* Blank or comment' : None,
        # line: Breakpoint <N> set in file <FILE>, line <LINE>.
        'Breakpoint (\d+) set in file (.*), line (\d+).' :
            lambda self, m: self.svc.emit('add_breakpoint', 
                                        ident=m.group(1), 
                                        file=m.group(2),
                                        line=m.group(3)),
        # line: Deleted breakpoint <N>
        'Deleted breakpoint (\d+)' :
            lambda self, m: self.svc.emit('del_breakpoint', ident=m.group(1)),
        # line: (<PATH>:<LINE>):  <FUNCTION>
        '\((.*):(\d+)\): (.*)' :
            lambda self, m: self.svc.emit('step', file=m.group(1), 
                                                  line=m.group(2), 
                                                  function=m.group(3)),
        '--Call--' : 
            lambda self, m: self.svc.emit('function_call'),
        '--Return--' : 
            lambda self, m: self.svc.emit('function_return')
    }
                
    def _parse(self, data):
        for pattern in self._parser_patterns:
            m = re.search(pattern, data)
            if m is not None:
                if self._parser_patterns[pattern] is not None:
                    self._parser_patterns[pattern](self,m)

    def _send_command(self,command):
        os.write(self._console.master, command + '\n')

    def _jump_to_line(self, event, data, foo=None):
        m = re.search('^\((.*):(.*)\):.*$', data)
        if m is not None:
            self.svc.boss.cmd('buffer', 'open_file', file_name=m.group(1))
            self.svc.boss.editor.cmd('goto_line', line=m.group(2))

    def init(self):
        gdb_path = self._dbg_param['path']
        self._console = self.svc.boss.cmd('commander','execute',
                                            commandargs=[gdb_path, 
                                "--cd="+self.svc._controller.get_cwd()],
                                            cwd=self.svc._controller.get_cwd(), 
                                            title='gdb',
                                            icon=None,
                                            use_python_fork=True,
                                            parser_func=self._parse)
        # match '(%%PATH%%:%%LINE%%):  <module>'
        self._console._term.match_add_callback('jump_to','^\(.*:.*\):.*$', 
                                                '^\((.*):(.*)\):.*$', self._jump_to_line)

        if self._executable is not None:
            self._send_command('file '+self._executable)
    
    def end(self):
        self._console.close_view()
        self._console = None
        self.svc.end_dbg_session()

    def start(self):
        """
        First time start: launch the debugger
        Second time start: continue debugging
        """
        if self._console == None:
            self.init()
            self._send_command('run')
        else:
            self._send_command('continue')

    __stop_state = False
    def stop(self):
        """
        First time stop: reinit the debugger
        Second time stop: end the debugger
        """
        if self._console == None:
            self.window.error_dlg('Tried to stop a non-working debugger')
        if self.__stop_state is False:
            self._send_command('run')
            self.__stop_state = True
        else:
            self.end()

    def step_in(self):
        self._send_command('step')

    def step_over(self):
        self._send_command('next')

    def finish(self):
        self._send_command('finish')

    def toggle_breakpoint(self, file, line):
        if (file, line) not in self._breakpoints:
            self._breakpoints.append((file, line))
            self.add_breakpoint(file, line)
        else:
            self._breakpoints.remove((file, line))
            self.del_breakpoint(file, line)
    
    def add_breakpoint(self, file, line):
        self._send_command('break '+file+':'+str(line))

    def del_breakpoint(self, file, line):
        self._send_command('clear '+file+':'+str(line))