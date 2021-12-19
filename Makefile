PI_IP_ADDRESS=10.0.2.224
PI_USERNAME=pi

.PHONY: run
run:
	@cd src && python3 app.py

.PHONY: install
install:
	@cd scripts && sudo bash install.sh

.PHONY: setup
setup:
	@cd scripts && sudo bash run_adafruit.sh

.PHONY: copy
copy:
	@echo "For development only"
	@rsync -a $(shell pwd) --exclude env --exclude training $(PI_USERNAME)@$(PI_IP_ADDRESS):/home/$(PI_USERNAME)

.PHONY: shell
shell:
	@echo "For development only"
	@ssh $(PI_USERNAME)@$(PI_IP_ADDRESS)

.PHONY: ping
ping:
	@ping $(PI_IP_ADDRESS)
