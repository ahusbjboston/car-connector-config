DOCKER_REPO="sec-rorschach-docker-local.artifactory.swg-devops.com"
DOCKER_URL="https://${DOCKER_REPO}"
DOCKER_IMAGE="cp4s-car-connector-config"
DOCKER_FULL_IMAGE="${DOCKER_REPO}/${DOCKER_IMAGE}:${TRAVIS_BUILD_ID}"

REPO_TO_RUN_IN="CAR/car-connector-config"

BRANCHES_TO_SCAN="develop"

SEC_SCANNER_DOCKER_REPO=${DOCKER_REPO}
SEC_SCANNER_DOCKER_IMAGE="q1-sitooling-sonar:1.1"
SEC_SCANNER_DOCKER_FULL_IMAGE="${SEC_SCANNER_DOCKER_REPO}/${SEC_SCANNER_DOCKER_IMAGE}"

function log()
{
   echo $(date -u) "[$LOG_PREFIX]: $1"
}

function run()
{
   $@ || exit 255
}

function sonar_scan()
{
  log "=============================="
  log "| Running SonarQube scanning |"
  log "=============================="

  run wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-3.2.0.1227-linux.zip
  run `which unzip` sonar-scanner-cli-3.2.0.1227-linux.zip -d /opt/sonarqube

  run /opt/sonarqube/sonar-scanner-3.2.0.1227-linux/bin/sonar-scanner \
          -Dsonar.projectKey="rorschach-car-connector-config" \
          -Dsonar.projectName="Car-Connector-Config-Services" \
          -Dsonar.branch.name="${TRAVIS_BRANCH}" \
          -Dsonar.sources="$(pwd)/src" \
          -Dsonar.exclusions="**/*.mock.js,**/*.test.js" \
          -Dsonar.log.level="DEBUG" \
          -Dsonar.host.url='http://9.21.121.107:9000' \
          -Dsonar.login=${SONARQUBE_TOKEN} \
          -Dsonar.projectBaseDir=$(pwd) \
          -Dsonar.dependencyCheck.reportPath=$(pwd)/scans/dependency-check-report.xml \
          -Dsonar.dependencyCheck.htmlReportPath=$(pwd)/scans/dependency-check-report.html \
          -Dsonar.javascript.lcov.reportPaths=$(pwd)/coverage/lcov.info \
          -Dsonar.projectVersion=${DATE}
}

function main()
{
  # log "Running docker login for ${DOCKER_FULL_IMAGE}"
  # run docker login -u="${ARTIFACTORY_USER}" -p="${ARTIFACTORY_PASSWORD}" "${DOCKER_URL}"

  # DATE=`date -u +%Y%m%d%H%M%S`
  if [ "${TRAVIS_REPO_SLUG}" == "${REPO_TO_RUN_IN}" ] ; then
    # log "Security scanning repo is ${REPO_TO_RUN_IN}"
    if [[ " ${BRANCHES_TO_SCAN[@]} " =~ " ${TRAVIS_BRANCH} " ]]; then
      if [ "${TRAVIS_PULL_REQUEST}" == "false" ] ; then
        sonar_scan
        # log "Creating scan output folder"
        # run mkdir -p scans

        # log "Running sonarqube scan"
        # run docker run -v $(pwd):$(pwd):rw "${SEC_SCANNER_DOCKER_FULL_IMAGE}"  \
        #   /opt/sonarqube/sonar-scanner-3.0.3.778-linux/bin/sonar-scanner \
        #   -Dsonar.projectKey="rorschach-investigate-backend" \
        #   -Dsonar.projectName="Investigate-Backend-Services" \
        #   -Dsonar.branch.name="${TRAVIS_BRANCH}" \
        #   -Dsonar.sources="$(pwd)/src" \
        #   -Dsonar.host.url='http://9.21.121.107:9000' \
        #   -Dsonar.login=${SONARQUBE_TOKEN} \
        #   -Dsonar.projectBaseDir=$(pwd) \
        #   -Dsonar.dependencyCheck.reportPath=$(pwd)/scans/dependency-check-report.xml \
        #   -Dsonar.dependencyCheck.htmlReportPath=$(pwd)/scans/dependency-check-report.html \
        #   -Dsonar.javascript.lcov.reportPaths=$(pwd)/coverage/lcov.info \
        #   -Dsonar.projectVersion=${DATE}
      else
        log "PR build so not scanning"
      fi
    else
      log "Branch ${TRAVIS_BRANCH} not in (${BRANCHES_TO_SCAN}) so not scanning"
    fi
  else
    log "Not publishing, repo is not ${REPO_TO_RUN_IN}"
  fi
}

main
