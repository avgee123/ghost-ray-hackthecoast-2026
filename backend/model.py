from roboflow import Roboflow
rf = Roboflow(api_key="yNrMXHJOacSwwBssyMlU")
project = rf.workspace("astrid-yoltc").project("taco-wikc7-gjcga")
version = project.version(1)
dataset = version.download("yolov8")