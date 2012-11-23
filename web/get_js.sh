#!/bin/sh
#This is a script to pull the required JS into the ./web dir, work in progress
wget http://download.dojotoolkit.org/release-1.7.0/dojo-release-1.7.0.tar.gz
tar zxvf dojo-release-1.7.0.tar.gz
rm dojo-release-1.7.0.tar.gz
ln -s dojo-release-1.7.0 dojo

###
wget https://github.com/documentcloud/underscore/tarball/1.2.2
tar zxvf 1.2.2
rm 1.2.2
ln -s documentcloud-underscore-8c34614 underscore

###
git clone https://github.com/AFDudley/btjs.git
wget http://jsclass.jcoglan.com/assets/JS.Class.3-0-8.zip
unzip JS.Class.3-0-8.zip
rm JS.Class.3-0-8.zip
ln -s JS.Class\ 3.0.8/ js.class

