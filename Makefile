run:
	python3 build.py
	trap 'kill 0' EXIT; \
	python3 -m http.server -d _public & \
	watchexec --ignore _public -- python3 build.py