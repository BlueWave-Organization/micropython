include("$(PORT_DIR)/boards/manifest.py")

freeze("$(BOARD_DIR)/my_code", "main.py")
freeze("$(BOARD_DIR)/my_code", "boot_sec.py")
freeze("$(BOARD_DIR)/my_code", "mylogo.py")