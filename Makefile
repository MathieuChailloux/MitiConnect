
PLUGINNAME=MitiConnect
ARCHIVE_DIR=$(PLUGINNAME)
ARCHIVE_NAME=$(PLUGINNAME).zip
TO_COPY_DIRS=algs help i18n icons steps ui
LIB_DIR=qgis_lib_mc
GRAPHAB_DIR=graphab4qgis
#SUBMODULE_DIRS=qgis_lib_mc graphab4qgis
#SUBMODULE_DIRS=qgis_lib_mc

GRAPHAB_EXE=

COMPILED_RESOURCE_FILES = resources.py

RESOURCE_SRC=$(shell grep '^ *<file' resources.qrc | sed 's@</file>@@g;s/.*>//g' | tr '\n' ' ')

COMMIT_ID = $(shell git rev-parse HEAD)
LIB_COMMIT = $(shell cd qgis_lib_mc; git rev-parse HEAD; cd ..)
GRAPHAB_COMMIT = $(shell cd graphab4qgis; git rev-parse HEAD; cd ..)
COMMIT_FILE = $(PLUGINNAME)/git-versions.txt

TESTCASES=

.PHONY: archive ui

default: compile

compile: $(COMPILED_RESOURCE_FILES)

%.py : %.qrc $(RESOURCES_SRC)
	pyrcc5 -o $*.py  $<

version-file:
	echo "$(PLUGINNAME) commit number "  > $(COMMIT_FILE)
	echo $(COMMIT_ID) >> $(COMMIT_FILE)
	echo "\nqgis_lib_mc commit number "  >> $(COMMIT_FILE)
	echo $(LIB_COMMIT) >> $(COMMIT_FILE)

archive:
	echo "Building delivery archive $(ARCHIVE_DIR)"
	rm -rf $(ARCHIVE_DIR)
	rm -f $(ARCHIVE_NAME)
	mkdir $(ARCHIVE_DIR)
	for d in $(TO_COPY_DIRS); do \
		cp -r $$d $(ARCHIVE_DIR) ; \
	done
	# LIB directory
	cp -r $(LIB_DIR) $(ARCHIVE_DIR)
	rm -rf $(ARCHIVE_DIR)/$(LIB_DIR)/.git
	rm -rf $(ARCHIVE_DIR)/$(LIB_DIR)/.gitignore
	# GRAPHAB directory
	cp -r $(GRAPHAB_DIR) $(ARCHIVE_DIR)
	rm -rf $(ARCHIVE_DIR)/$(GRAPHAB_DIR)/.git
	rm -rf $(ARCHIVE_DIR)/$(GRAPHAB_DIR)/.gitignore
	rm -f $(ARCHIVE_DIR)/$(GRAPHAB_DIR)/README.md
	rm -f $(ARCHIVE_DIR)/$(GRAPHAB_DIR)/LICENSE
	rm -f $(ARCHIVE_DIR)/$(GRAPHAB_DIR)/pylintrc
	rm -f $(ARCHIVE_DIR)/$(GRAPHAB_DIR)/metadata.txt
	rm -f $(ARCHIVE_DIR)/$(GRAPHAB_DIR)/processing/graphab-2.8.0.jar
	#rm -rf $(ARCHIVE_DIR)/$(GRAPHAB_DIR)/README.md
	#rm -f $(ARCHIVE_DIR)/graphab4qgis/
	# for d in $(TESTCASES); do \
		# rm -rf $(ARCHIVE_DIR)/sample_data/EPCI_Clermontais_2012/$$d/outputs ; \
		# rm -rf $(ARCHIVE_DIR)/sample_data/EPCI_Clermontais_2012/$$d/tmp ; \
	# done
#	rm -rf $(ARCHIVE_DIR)/sample_data/EPCI_Clermontais_2012/CBC/outputs
#	rm -rf $(ARCHIVE_DIR)/sample_data/EPCI_Clermontais_2012/CBC/tmp
#	rm -rf $(ARCHIVE_DIR)/sample_data/EPCI_Clermontais_2012/CUT/outputs
#	rm -rf $(ARCHIVE_DIR)/sample_data/EPCI_Clermontais_2012/CUT/tmp
	mkdir $(ARCHIVE_DIR)/docs
	# cp docs/FragScape_UserGuide_en.pdf $(ARCHIVE_DIR)/docs
	cp *.py $(ARCHIVE_DIR)
	#cp *.ui $(ARCHIVE_DIR)
	cp *.md $(ARCHIVE_DIR)
	cp LICENSE $(ARCHIVE_DIR)
	cp metadata.txt $(ARCHIVE_DIR)
	#rm -f $(ARCHIVE_DIR)/resources.py
	#cp resources.qrc $(ARCHIVE_DIR)
	echo "$(PLUGINNAME) commit number "  > $(COMMIT_FILE)
	echo $(COMMIT_ID) >> $(COMMIT_FILE)
	echo "\nqgis_lib_mc commit number "  >> $(COMMIT_FILE)
	echo $(LIB_COMMIT) >> $(COMMIT_FILE)
	echo $(GRAPHAB_COMMIT) >> $(COMMIT_FILE)
	zip -r $(ARCHIVE_NAME) $(ARCHIVE_DIR)
	rm -rf $(ARCHIVE_DIR)

ui:
	pyuic5 -o ui/miti_connect_dialog_base.py ui/miti_connect_dialog_base.ui
	pyuic5 -o ui/vector_data_dialog_ui.py ui/vector_data_dialog.ui
	pyuic5 -o ui/raster_data_dialog_ui.py ui/raster_data_dialog.ui
	pyuic5 -o ui/landuse_dialog_ui.py ui/landuse_dialog.ui
	pyuic5 -o ui/species_dialog_ui.py ui/species_dialog.ui
	pyuic5 -o ui/scenario_dialog_ui.py ui/scenario_dialog.ui
