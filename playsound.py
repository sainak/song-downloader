# CREDITS:TaylorSMarks
# https://github.com/TaylorSMarks/playsound/blob/master/playsound.py


from platform import system


class PlaysoundException(Exception):
    pass


def _playsoundWin(sound):

    from ctypes import c_buffer, windll
    from random import random
    from sys import getfilesystemencoding

    def winCommand(*command):
        buf = c_buffer(255)
        command = " ".join(command).encode(getfilesystemencoding())
        errorCode = int(windll.winmm.mciSendStringA(command, buf, 254, 0))
        if errorCode:
            errorBuffer = c_buffer(255)
            windll.winmm.mciGetErrorStringA(errorCode, errorBuffer, 254)
            exceptionMessage = (
                "\n    Error " + str(errorCode) + " for command:"
                "\n        " + command.decode() + "\n    " + errorBuffer.value.decode()
            )
            raise PlaysoundException(exceptionMessage)
        return buf.value

    alias = "playsound_" + str(random())
    winCommand('open "' + sound + '" alias', alias)
    winCommand("set", alias, "time format milliseconds")
    durationInMS = winCommand("status", alias, "length")
    winCommand("play", alias, "from 0 to", durationInMS.decode())


def _playsoundOSX(sound):

    from AppKit import NSSound
    from Foundation import NSURL
    from time import sleep

    url = NSURL.URLWithString_(sound)
    nssound = NSSound.alloc().initWithContentsOfURL_byReference_(url, True)
    if not nssound:
        raise IOError("Unable to load sound named: " + sound)
    nssound.play()


def _playsoundNix(sound, block=True):

    from urllib.request import pathname2url

    import gi

    gi.require_version("Gst", "1.0")
    from gi.repository import Gst

    Gst.init(None)

    playbin = Gst.ElementFactory.make("playbin", "playbin")
    playbin.props.uri = sound

    set_result = playbin.set_state(Gst.State.PLAYING)

    if set_result != Gst.StateChangeReturn.ASYNC:
        raise PlaysoundException("playbin.set_state returned " + repr(set_result))
    bus = playbin.get_bus()

    bus.poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)
    playbin.set_state(Gst.State.NULL)


system = system()

if system == "Windows":
    playsound = _playsoundWin
elif system == "Darwin":
    playsound = _playsoundOSX
else:
    playsound = _playsoundNix

del system
