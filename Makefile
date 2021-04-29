SHELL := /bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
UI_PORT=60125

run:
	docker-compose up

stop:
	docker-compose down

define create_desktop_shortcut
	@echo "$(1)" > $${HOME}/.local/share/applications/$(2)
	@echo "$(1)" > $${HOME}/Desktop/$(2)
	chmod +x $${HOME}/.local/share/applications/$(2)
	chmod +x $${HOME}/Desktop/$(2)
	gio set $${HOME}/.local/share/applications/$(2) metadata::trusted true
	gio set $${HOME}/Desktop/$(2) metadata::trusted true
endef


define CLUB_CONTROLLER_SERVER_DESKTOP
[Desktop Entry]
Type=Application
Name=Club Controller Server
GenericName=Club Controller Server
Name[en_US]=Club Controller Server
Comment=The one to control them all
Icon=$(ROOT_DIR)/icon.png
Exec=bash -c "cd $(ROOT_DIR)/server/ && bash $(ROOT_DIR)/server/server.sh"
Terminal=true
Categories=Electronics;
endef

define CLUB_CONTROLLER_UI_DESKTOP
[Desktop Entry]
Type=Application
Name=Club Controller UI Web Server
GenericName=Club Controller UI Web Server
Name[en_US]=Club Controller UI Web Server
Comment=Web server for hosting the the UI as a web app on this machine
Icon=$(ROOT_DIR)/icon.png
Exec=bash -c "cd $(ROOT_DIR)/ui && bash $(ROOT_DIR)/ui/web_server/server.sh"
Terminal=true
Categories=Electronics;
endef

define CLUB_CONTROLLER_COMPLETE
[Desktop Entry]
Type=Application
Name=Club Controller Complete
GenericName=Club Controller Complete
Name[en_US]=Club Controller Complete
Comment=The one to control them all
Icon=$(ROOT_DIR)/icon.png
Exec=bash -c 'cd $(ROOT_DIR)/server/ && $(ROOT_DIR)/server/server.sh & cd $(ROOT_DIR)/ui && $(ROOT_DIR)/ui/web_server/server.sh & chromium-browser --app=http://localhost:$(UI_PORT) --start-fullscreen & exec $(SHELL)'
Terminal=true
Categories=Electronics;
endef

export CLUB_CONTROLLER_SERVER_DESKTOP
install-desktop-shortcut-server:
	$(call create_desktop_shortcut, $$CLUB_CONTROLLER_SERVER_DESKTOP,club_controller_server.desktop)

export CLUB_CONTROLLER_UI_DESKTOP
install-desktop-shortcut-ui:
	$(call create_desktop_shortcut, $$CLUB_CONTROLLER_UI_DESKTOP,club_controller_ui.desktop)

export CLUB_CONTROLLER_COMPLETE
install-desktop-shortcut-complete:
	$(call create_desktop_shortcut, $$CLUB_CONTROLLER_COMPLETE,club_controller_complete.desktop)
