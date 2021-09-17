
PLUGINNAME=ERC-TVB
ARCHIVE_DIR=$(PLUGINNAME)
ARCHIVE_NAME=$(PLUGINNAME).zip
TO_COPY_DIRS=algs help i18n icons sample_data steps
MC_LIB_DIR=qgis_lib_mc

COMPILED_RESOURCE_FILES = resources.py

RESOURCE_SRC=$(shell grep '^ *<file' resources.qrc | sed 's@</file>@@g;s/.*>//g' | tr '\n' ' ')

COMMIT_ID = $(shell git rev-parse HEAD)
LIB_COMMIT = $(shell cd qgis_lib_mc; git rev-parse HEAD; cd ..)
COMMIT_FILE = $(PLUGINNAME)/git-versions.txt

TESTCASES=

.PHONY: archive

default: compile

compile: $(COMPILED_RESOURCE_FILES)

%.py : %.qrc $(RESOURCES_SRC)
	pyrcc5 -o $*.py  $<

version-file:
	echo "FragScape commit number "  > $(COMMIT_FILE)
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
	cp -r $(MC_LIB_DIR) $(ARCHIVE_DIR)
	cp *.py $(ARCHIVE_DIR)
	cp *.ui $(ARCHIVE_DIR)
	cp *.md $(ARCHIVE_DIR)
	cp LICENSE $(ARCHIVE_DIR)
	cp metadata.txt $(ARCHIVE_DIR)
	cp resources.qrc $(ARCHIVE_DIR)
	echo "$(PLUGINNAME) commit number "  > $(COMMIT_FILE)
	echo $(COMMIT_ID) >> $(COMMIT_FILE)
	echo "\nqgis_lib_mc commit number "  >> $(COMMIT_FILE)
	echo $(LIB_COMMIT) >> $(COMMIT_FILE)
	zip -r $(ARCHIVE_NAME) $(ARCHIVE_DIR)
	rm -rf $(ARCHIVE_DIR)

ui:
	pyuic5 -o erc_tvb_plugin_dialog.py erc_tvb_plugin_dialog.ui