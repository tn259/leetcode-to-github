#!/bin/bash -e

##########
# Install non python dependencies such as Geckodriver
##########

set -x

function install_geckodriver() {

  #
  # Download Geckodriver to current directory
  #

  GECKODRIVER_VERSION="v0.26.0"
  GECKODRIVER_TARGZ="geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz"

  wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/$GECKODRIVER_TARGZ 

  tar -xzvf $GECKODRIVER_TARGZ

  # Should have a geckodriver binary by now
  # copy to ~/.local/bin for user specific "install"
  cp geckodriver /usr/local/bin/
}

install_geckodriver 
