'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from threading import Thread, Lock
import pygetwindow as gw
from pynput import mouse, keyboard
from datetime import datetime
from pynput.keyboard import Key
from pm4py.objects.log.obj import Event
import time
import psutil
import win32process
import os
from PIL import ImageGrab


class WindowsEventLogger(Thread):
    def __init__(self, event_stream, context_keys=None, screenshots_folder=None):
        """
        Keyboard and mouse click recorder for Windows. This is useful for task mining purposes.

        Parameters
        ----------
        event_stream
            Event stream that should be used to record the events
        context_keys
            (if provided) list of keyboard keys to be considered context-switching (default:
            {Key.tab, Key.enter, Key.esc, Key.f1, Key.f2, Key.f3, Key.f4, Key.f5, Key.f6, Key.f7,
                                 Key.f8, Key.f9, Key.f10, Key.f11, Key.f12, Key.f13, Key.f14, Key.f15, Key.f16, Key.f16,
                                 Key.f17, Key.f18, Key.f19, Key.f20, Key.home, Key.end}
            )
        screenshots_folder
            (if provided) folder in which the screenshots shall be saved

        Minimum Viable Example:

            from pm4py.streaming.stream.live_event_stream import LiveEventStream
            from pm4py.streaming.connectors.windows.click_key_logger import WindowsEventLogger
            from pm4py.streaming.util.event_stream_printer import EventStreamPrinter
            import time

            stream = LiveEventStream()
            wel = WindowsEventLogger(stream, screenshots_folder="output")
            printer = EventStreamPrinter()
            stream.register(printer)
            stream.start()
            wel.start()

            print("listening")

            # listen only for 5 seconds
            time.sleep(5)

            wel.stop()
            stream.stop()

            print("stopped")
        """
        Thread.__init__(self)

        self.event_stream = event_stream
        self.lock = Lock()
        self.context_keys = context_keys
        if self.context_keys is None:
            self.context_keys = {Key.tab, Key.enter, Key.esc, Key.f1, Key.f2, Key.f3, Key.f4, Key.f5, Key.f6, Key.f7,
                                 Key.f8, Key.f9, Key.f10, Key.f11, Key.f12, Key.f13, Key.f14, Key.f15, Key.f16, Key.f16,
                                 Key.f17, Key.f18, Key.f19, Key.f20, Key.home, Key.end}

        self.screenshots_folder = screenshots_folder
        if self.screenshots_folder is not None:
            if not os.path.exists(self.screenshots_folder):
                os.mkdir(self.screenshots_folder)

        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_release=self.on_key_release)

    def run(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

        self.mouse_listener.join()
        self.keyboard_listener.join()

    def stop(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def get_process_name(self, hwnd):
        """Fetch the process name using the window handle."""
        try:
            # Get the process ID associated with the handle
            hwnd = gw.getActiveWindow()._hWnd
            threadid, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name()
        except (psutil.NoSuchProcess, IndexError):
            return None

    def record(self, windows_title, process_name=None, x=None, y=None, button=None, key=None):
        self.lock.acquire()

        process_name = str(process_name) if process_name is not None else ""
        x = str(x) if x is not None else ""
        y = str(y) if y is not None else ""
        button = str(button) if button is not None else ""
        key = str(key) if key is not None else ""

        timestamp = time.time()
        dt_object = datetime.utcfromtimestamp(timestamp)

        image_path = ""
        img = None

        if self.screenshots_folder is not None:
            image_path = os.path.join(self.screenshots_folder, "screenshot_%s.png" % (
                    dt_object.strftime('%Y%m%d_%H%M%S') + '_' + dt_object.strftime('%f')[:3]))

        event = Event(
            {"timestamp": "NONE", "windows_title": windows_title, "process_name": process_name, "x": x, "y": y,
             "button": button, "key": key, "screenshot": image_path})
        self.event_stream.append(event)

        if image_path:
            img = ImageGrab.grab(all_screens=True)

        self.lock.release()

        if image_path:
            img.save(image_path, "PNG")

    def on_click(self, x, y, button, pressed):
        if pressed:
            # Introduce a short delay to allow window context switch
            time.sleep(0.1)

            # Get the title of the now active window
            window_title = gw.getActiveWindow().title

            # Get the process name using the window handle
            process_name = self.get_process_name(gw.getActiveWindow()._hWnd)

            self.record(window_title, process_name=process_name, x=x, y=y, button=button)

    def on_key_release(self, key):
        # Check if the released key is in the list
        if key in self.context_keys:
            # Get the title of the active window
            window_title = gw.getActiveWindow().title

            # Get the process name using the window handle
            process_name = self.get_process_name(gw.getActiveWindow()._hWnd)

            self.record(window_title, process_name=process_name, key=key)
