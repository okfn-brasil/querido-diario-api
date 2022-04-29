#!/bin/bash

# This script should be used to bump new versions. It will create a git tag for 
# the new version and it will update the Helm Chart used to deploy the app in 
# Kubernetes.

get_latest_version() {
	git describe --tags
}

latest_version=`get_latest_version`
if [ ! $? -eq 0 ]; then
	echo "Cannot find any previous version. Please, check if there is some version tag."
	exit 1
fi
echo "Latest version detected $latest_version"

major=`echo $latest_version | sed 's/^v//g'  | sed 's/-.*$//' | sed 's/+.*$//'| awk '{split($0,version,"."); print version[1]}'`
minor=`echo $latest_version | sed 's/^v//g'  | sed 's/-.*$//' | sed 's/+.*$//'| awk '{split($0,version,"."); print version[2]}'`
patch=`echo $latest_version | sed 's/^v//g'  | sed 's/-.*$//' | sed 's/+.*$//'| awk '{split($0,version,"."); print version[3]}'`

minor=$(($minor+1))

new_version="$major.$minor.$patch"
echo "New version: $new_version"

echo "Creating new git tag."
git tag $new_version -m "Version bump: $new_version"

echo "Updating app version in the helm chart."
sed -i "s/^appVersion:.*/appVersion: $new_version/" helm/Chart.yaml

echo ""
echo "Now you need to commit the changes! ;)"
