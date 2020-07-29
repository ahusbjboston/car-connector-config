#!/bin/bash

LOG_PREFIX=`basename "$0"`

function log()
{
	echo $(date -u) "[$LOG_PREFIX]: $1"
}

function run()
{
   $@ || exit 255
}

function main()
{
	log "Running before_install.sh"

	log "Running Setup .npmrc"

  # Replace ARTIFACTORY_USERNAME and ARTIFACTORY_API_KEY with your values.
  # curl -u "${ARTIFACTORY_USERNAME}:${ARTIFACTORY_API_KEY}" https://na.artifactory.swg-devops.com/artifactory/api/npm/auth/ >> .npmrc
  curl -u "${ARTIFACTORY_USER}:${ARTIFACTORY_API_KEY}" https://na.artifactory.swg-devops.com/artifactory/api/npm/sec-uds-npm-virtual/auth/ibm-security >> .npmrc
  curl -u "${ARTIFACTORY_USER}:${ARTIFACTORY_API_KEY}" https://na.artifactory.swg-devops.com/artifactory/api/npm/sec-common-npm-local/auth/ibm-security >> .npmrc
  curl -u "${ARTIFACTORY_USER}:${ARTIFACTORY_API_KEY}" https://na.artifactory.swg-devops.com/artifactory/api/npm/res-ibma-npm-local/auth/ibma >> .npmrc
  curl -u "${ARTIFACTORY_USER}:${ARTIFACTORY_API_KEY}" https://na.artifactory.swg-devops.com/artifactory/api/npm/sec-rorschach-npm-local/auth/isc >> .npmrc
  # Specify registry for packages that use the `@isc` scope.
  # echo 'registry=https://na.artifactory.swg-devops.com/artifactory/api/npm/sec-rorschach-npm-virtual/' >> .npmrc  

}

main
