
import sys
import uuid
import argparse

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

from sources import RTSP, FILES
from timer import Timer

GObject.threads_init()
Gst.init(sys.argv)
# Gst.debug_set_active(True)
# Gst.debug_set_default_threshold(5)

ap = argparse.ArgumentParser()
ap.add_argument("-n", "--number", required=True, help="Pipeline count")
ap.add_argument("--rtsp", action='store_true', help="Indicates rtspsrc pipeline")
ap.add_argument("--file", action='store_true', help="Indicates filesrc pipeline")
args = vars(ap.parse_args())


def random_id():
    return uuid.uuid1().urn[9:]


def stop(loop):
    loop.quit()


def on_fps(element, fps, droprate, avgfps):
    print("{} {}".format(fps, avgfps))

RUN_TIME = 10  # seconds

pipe_from_file = "filesrc name={} ! decodebin ! videoconvert \
                 ! video/x-raw,format=RGB ! videoconvert ! fpsdisplaysink name={} video-sink=fakesink sync=false"

pipe_from_rtsp = "rtspsrc name={} drop-on-latency=true ! decodebin ! videoconvert \
                 ! video/x-raw,format=RGB ! videoconvert ! fpsdisplaysink name={} video-sink=fakesink sync=false"

pipeline_count = int(args['number'])
assert pipeline_count > 0

pipe_command = pipe_from_rtsp if args['rtsp'] else pipe_from_file
sources = RTSP if args['rtsp'] else FILES

uniques = [random_id() for _ in range(pipeline_count)]
fps_names = ["fps" + idx for idx in uniques]
sources_names = ["src" + idx for idx in uniques]
commands = [pipe_command.format(src, fps) for src, fps in zip(sources_names, fps_names)]

pipelines = [Gst.parse_launch(cmd) for cmd in commands]

for i, p in enumerate(pipelines):
    src = p.get_by_name(sources_names[i])
    assert src is not None
    src.set_property("location", sources[i])

    fps = p.get_by_name(fps_names[i])
    assert fps is not None
    fps.set_property("signal-fps-measurements", True)
    fps.connect('fps-measurements', on_fps)
    p.set_state(Gst.State.PLAYING)

mainloop = GObject.MainLoop()

timer = Timer(RUN_TIME, lambda: stop(mainloop))
try:
    timer.start()
    # print("Started pipeline. Wait {} sec".format(RUN_TIME))
    mainloop.run()
except:
    pass

timer.cancel()
for p in pipelines:
    p.set_state(Gst.State.NULL)
# print("Done")