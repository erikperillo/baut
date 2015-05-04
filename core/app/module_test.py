import app

e = app.Extractor("filter.sh",key="perf")

e.run(["stat","echo","hue"])

e.filter()

