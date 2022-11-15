
PLUGINNAME=MitiConnect
ARCHIVE_DIR=$(PLUGINNAME)
ARCHIVE_NAME=$(PLUGINNAME).zip
TO_COPY_DIRS=algs help i18n icons steps ui
SUBMODULE_DIRS=qgis_lib_mc graphab4qgis

GRAPHAB_EXE=

COMPILED_RESOURCE_FILES = resources.py

RESOURCE_SRC=$(shell grep '^ *<file' resources.qrc | sed 's@</file>@@g;s/.*>//g' | tr '\n' ' ')

COMMIT_ID = $(shell git rev-parse HEAD)
LIB_COMMIT = $(shell cd qgis_lib_mc; git rev-parse HEAD; cd ..)
GRAPHAB_COMMIT = $(shell cd graphab4qgis; git rev-parse HEAD; cd ..)
COMMIT_FILE = $(PLUGINNAME)/git-versions.txt

TESTCASES=

.PHONY: archive

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
	for d in $(SUBMODULE_DIRS); do \
		cp -r $$d $(ARCHIVE_DIR) ; \
		rm -rf $(ARCHIVE_DIR)/$$d/.git ; \
		rm -f $(ARCHIVE_DIR)/$$d/.gitignore ; \
	done
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
	rm -f $(ARCHIVE_DIR)/resources.py
	#cp resources.qrc $(ARCHIVE_DIR)
	echo "$(PLUGINNAME) commit number "  > $(COMMIT_FILE)
	echo $(COMMIT_ID) >> $(COMMIT_FILE)
	echo "\nqgis_lib_mc commit number "  >> $(COMMIT_FILE)
	echo $(LIB_COMMIT) >> $(COMMIT_FILE)
	echo $(GRAPHAB_COMMIT) >> $(COMMIT_FILE)
	zip -r $(ARCHIVE_NAME) $(ARCHIVE_DIR)
	rm -rf $(ARCHIVE_DIR)

ui:
	pyuic5 -o MitiConnect_dialog.py MitiConnect_dialog.ui
