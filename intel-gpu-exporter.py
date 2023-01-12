import json
import string
import subprocess
import time
import argparse

from prometheus_client import (GC_COLLECTOR, PLATFORM_COLLECTOR,
                               PROCESS_COLLECTOR, REGISTRY, Metric,
                               start_http_server)


class DataCollector(object):
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def collect(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--device", help = "Device filter to select Intel GPU to monitor")
        args = parser.parse_args()
        
        if args.device:
            cmd = "/usr/bin/timeout -k 2 2 /usr/bin/intel_gpu_top -J -d %s" % args.device
        else:
            cmd = "/usr/bin/timeout -k 2 2 /usr/bin/intel_gpu_top -J"
        
        raw_output = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")
        output = f"[{raw_output.translate(str.maketrans('', '', string.whitespace))}]"
        data = json.loads(output)

        render_busy_percent = data[1]["engines"]["Render/3D/0"]["busy"]
        metric = Metric("intel_gpu_render_busy_percent", "Render engine busy utilisation in %", "summary")
        metric.add_sample("intel_gpu_render_busy_percent", value=render_busy_percent, labels={})
        yield metric

        video_0_busy_percent = data[1]["engines"]["Video/0"]["busy"]
        metric = Metric("intel_gpu_video_0_busy_percent", "Video 0 engine busy utilisation in %", "summary")
        metric.add_sample("intel_gpu_video_0_busy_percent", value=video_0_busy_percent, labels={})
        yield metric

        video_1_busy_percent = data[1]["engines"]["Video/1"]["busy"]
        metric = Metric("intel_gpu_video_1_busy_percent", "Video 1 engine busy utilisation in %", "summary")
        metric.add_sample("intel_gpu_video_1_busy_percent", value=video_1_busy_percent, labels={})
        yield metric

        enhance_0_busy_percent = data[1]["engines"]["VideoEnhance/0"]["busy"]
        metric = Metric("intel_gpu_enhance_0_busy_percent", "Enhance 0 engine busy utilisation in %", "summary")
        metric.add_sample("intel_gpu_enhance_0_busy_percent", value=enhance_0_busy_percent, labels={})
        yield metric

        if 'VideoEnhance/1' not in data[1]["engines"]:
            enhance_1_busy_percent = "0.0"
        else:
            enhance_1_busy_percent = data[1]["engines"]["VideoEnhance/1"]["busy"]
            
        metric = Metric("intel_gpu_enhance_1_busy_percent", "Enhance 1 engine busy utilisation in %", "summary")
        metric.add_sample("intel_gpu_enhance_1_busy_percent", value=enhance_1_busy_percent, labels={})
        yield metric

if __name__ == "__main__":
    host, port = "0.0.0.0:8080".split(':')
    start_http_server(int(port), host)
    REGISTRY.unregister(PROCESS_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.register(DataCollector(f"http://{host}:{port}/metrics"))
    while True:
        time.sleep(1)
