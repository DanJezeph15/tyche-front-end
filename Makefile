.PHONY: install
install:
	@pip install --progress-bar off -r requirements.txt

.PHONY: install-dev
install-dev:
	make install
	@pip install --progress-bar off -U devtools