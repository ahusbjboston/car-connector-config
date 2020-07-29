#!/bin/bash
LOG_PREFIX=`basename "$0"`

DOCKER_REPO="sec-rorschach-docker-local.artifactory.swg-devops.com"
DOCKER_URL="https://${DOCKER_REPO}"
DOCKER_IMAGE="cp4s-car-connector-config"
DOCKER_FULL_IMAGE="${DOCKER_REPO}/${DOCKER_IMAGE}:${TRAVIS_BUILD_ID}"

function log()
{
   echo $(date -u) "[$LOG_PREFIX]: $1"
}

function run()
{
   $@ || exit 255
}

# Barely Working Verification
function BWV() 
{
  log "==========================================="
  log "|Running BWV (Barely Working Verification)|"
  log "==========================================="
  log "start api server in docker container"
  run docker run -d -p 3000:3000/tcp --name "${DOCKER_IMAGE}" "${DOCKER_FULL_IMAGE}"
  while [ $(docker logs ${DOCKER_IMAGE} | grep -c "api server") -lt 1  ]; do echo "waiting.."; sleep 1; ((c++)) && ((c==10)) && break; done

  status=$(curl localhost:3000/liveness)

  docker kill "${DOCKER_IMAGE}"
  docker rm "${DOCKER_IMAGE}"
  log "Running docker logout for ${DOCKER_FULL_IMAGE}"
  docker logout "${DOCKER_URL}"

  if [ "$status" != "OK" ]
  then
    log "failed BWV. check log for more information"
    exit 1
  fi
}





function main()
{

  log "Running npm test"
  run npm run test

  log "Running npm build"
  run npm run build

  log "Running docker login for ${DOCKER_FULL_IMAGE}"
  run docker login -u="${ARTIFACTORY_USER}" -p="${ARTIFACTORY_PASSWORD}" "${DOCKER_URL}"

  log "Running docker build for ${DOCKER_FULL_IMAGE}"
  run docker build -t "${DOCKER_FULL_IMAGE}" . 

  BWV # "Running Barely Working Verification"

}

main
