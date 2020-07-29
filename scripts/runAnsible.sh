#!/bin/bash
# cp -R ./node_modules/@isc/car-devops ./car-devops 

cp -R ./scripts/car-devops ./car-devops 

echo "$ANSIBLE_VAULT_PASSWORD" > vault_pass
build_type="origin_push"
commit_id="$TRAVIS_COMMIT"
echo "Initial build info"
echo "Build number is: ${TRAVIS_BUILD_NUMBER}"
echo "TRAVIS_REPO_SLUG is ${TRAVIS_REPO_SLUG}" 
echo "TRAVIS_BRANCH is ${TRAVIS_BRANCH}"
echo "TRAVIS_BUILD_DIR is ${TRAVIS_BUILD_DIR}"
echo "TRAVIS_TAG is $TRAVIS_TAG"
echo "commit range: ${TRAVIS_COMMIT_RANGE}"
echo "Commit id is: $commit_id"
# matching branches: Relite or release-... or rel-...
release_branch_regex="^(rel|release|Relite)/[0-9]\.[0-9]\.[0-9]+"
feature_branch_regex="^(feat|feature|fb)/\w+"
fixpack_branch_regex="^(fp|fixpack)/[0-9]\.[0-9]\.[0-9]+"
RELEASE_VERSION=`echo ${TRAVIS_BRANCH} | rev | cut -d '/' -f1 | rev`
echo "Release version is: ${RELEASE_VERSION}"

# if we are in the main repo
if [[ "${TRAVIS_REPO_SLUG}" == "CAR/car-connector-config" ]]; then
    echo "We are in the main repo"
    if [[ ${TRAVIS_BRANCH} =~ $release_branch_regex ]];then
        echo "We are in a release branch"
        if [[ "${TRAVIS_EVENT_TYPE}" == "push" ]]; then
            echo "We are in a push type so image will be created"
            # In case of any failure or conflict in semantic release we can enable the following line
            build_type="upstream_relite_tag"
            # build_type="upstream_release_push"

        elif [[ "${TRAVIS_EVENT_TYPE}" == "pull_request" ]]; then
            echo "We are in a pull req type so some check will be run on the code"
            build_type="upstream_release_pr"
        fi
    elif [[ ${TRAVIS_BRANCH} =~ $feature_branch_regex ]];then
    echo "We are in a feature branch"
        if [[ "${TRAVIS_EVENT_TYPE}" == "push" ]]; then
            echo "We are in a push type so image ft-xxx will be created"
            # In case of any failure or conflict in semantic release we can enable the following line
            # build_type="upstream_relite_tag"
            build_type="upstream_ft_push"

        elif [[ "${TRAVIS_EVENT_TYPE}" == "pull_request" ]]; then
            echo "We are in a pull req type so some check will be run on the code"
            build_type="upstream_ft_pr"
        fi
    elif [[ ${TRAVIS_BRANCH} =~ $fixpack_branch_regex ]];then
        echo "We are in a fixpack branch"
        if [[ "${TRAVIS_EVENT_TYPE}" == "push" ]]; then
            echo "We are in a push type so image fp_{git commit}_{increment} will be created"
            # In case of any failure or conflict in semantic release we can enable the following line
            build_type="upstream_fp_push"

        elif [[ "${TRAVIS_EVENT_TYPE}" == "pull_request" ]]; then
            echo "We are in a pull req type so some check will be run on the code"
            build_type="upstream_fp_pr"
        fi    
    elif [[ "${TRAVIS_BRANCH}" == "master" ]]; then
        if [[ "${TRAVIS_EVENT_TYPE}" == "push" ]]; then
            build_type="upstream_release_push"
        elif [[ "${TRAVIS_EVENT_TYPE}" == "pull_request" ]]; then
            build_type="upstream_release_pr"
        fi   
    elif [[ "${TRAVIS_BRANCH}" == "develop" ]]; then
        if [[ "${TRAVIS_EVENT_TYPE}" == "push" ]]; then
            build_type="upstream_develop_push"
        elif [[ "${TRAVIS_EVENT_TYPE}" == "pull_request" ]]; then
            build_type="upstream_develop_pr"
        fi
    elif [[ "${TRAVIS_BRANCH}" == "devite" ]]; then
        if [[ "${TRAVIS_EVENT_TYPE}" == "push" ]]; then
            build_type="upstream_devite_push"
        elif [[ "${TRAVIS_EVENT_TYPE}" == "pull_request" ]]; then
            build_type="upstream_devite_pr"
        fi
    elif [[ "${TRAVIS_BRANCH}" == "relite" ]]; then
        if [[ "${TRAVIS_EVENT_TYPE}" == "push" ]]; then
            build_type="upstream_relite_push"
        elif [[ "${TRAVIS_EVENT_TYPE}" == "pull_request" ]]; then
            build_type="upstream_relite_pr"
        fi
    elif [[ "${TRAVIS_BRANCH}" == "car-sanity-check" ]]; then
        if [[ "${TRAVIS_EVENT_TYPE}" == "push" ]]; then
            build_type="upstream_car_sanity_check_push"
        elif [[ "${TRAVIS_EVENT_TYPE}" == "pull_request" ]]; then
            build_type="upstream_car_sanity_check_pr"
        fi
    elif [[ "${TRAVIS_BRANCH}" == "$TRAVIS_TAG" ]]; then
        echo
        build_type="upstream_relite_tag"
    else
        echo "Travis Builds will run for (develop, devite, relite, car-sanity-check and release-x.x.x or rel-x.x.x) branches only! exiting..."
        exit 0
    fi
    echo "Travis Branch is: ${TRAVIS_BRANCH} and build type is ${build_type}"
    # run the respective commands 
    if [[ -z "$TRAVIS_TAG" ]]; then
        echo "[[ -z TRAVIS_TAG ]] is true: $TRAVIS_TAG so no tagging will be executed"
        if [[ "${TRAVIS_BRANCH}" == "develop" ]] || [[ "${TRAVIS_BRANCH}" == "devite" ]] || [[ "${build_type}" == "relite" ]]; then
            ansible-playbook -i ./car-devops/inventory/"${TRAVIS_BRANCH}" ./car-devops/playbooks/car-connector-config.yml -vv --extra-vars '{"build_type":"'"${build_type}"'", "TRAVIS_BUILD_DIR":"'"${TRAVIS_BUILD_DIR}"'","TRAVIS_BUILD_NUMBER":"'"${TRAVIS_BUILD_NUMBER}"'", "TRAVIS_BRANCH":"'"${TRAVIS_BRANCH}"'", "COMMIT_ID":"'"${commit_id}"'", "RELEASE_VERSION":"'"${RELEASE_VERSION}"'"}' --vault-password-file vault_pass
        elif [[ ${TRAVIS_BRANCH} =~ $feature_branch_regex ]]; then
            echo "Running ansible for feature branch"
            ansible-playbook -i ./car-devops/inventory/develop ./car-devops/playbooks/car-connector-config.yml -vv --extra-vars '{"build_type":"'"${build_type}"'", "TRAVIS_BUILD_DIR":"'"${TRAVIS_BUILD_DIR}"'","TRAVIS_BUILD_NUMBER":"'"${TRAVIS_BUILD_NUMBER}"'", "TRAVIS_BRANCH":"'"${TRAVIS_BRANCH}"'", "COMMIT_ID":"'"${commit_id}"'", "RELEASE_VERSION":"'"${RELEASE_VERSION}"'"}' --vault-password-file vault_pass
        else
            # at this point does not matter which inventory we are passing so we pass relite. We are in Sanity check
            echo "we are using relite inventory"
            ansible-playbook -i ./car-devops/inventory/relite ./car-devops/playbooks/car-connector-config.yml -vv --extra-vars '{"build_type":"'"${build_type}"'", "TRAVIS_BUILD_DIR":"'"${TRAVIS_BUILD_DIR}"'","TRAVIS_BUILD_NUMBER":"'"${TRAVIS_BUILD_NUMBER}"'", "TRAVIS_BRANCH":"'"${TRAVIS_BRANCH}"'", "COMMIT_ID":"'"${commit_id}"'", "RELEASE_VERSION":"'"${RELEASE_VERSION}"'"}' --vault-password-file vault_pass
        fi    
    else
        echo "[[ -z TRAVIS_TAG ]] is false: $TRAVIS_TAG so tagging will be executed"
        # ansible-playbook -i ./car-devops/inventory/relite ./car-devops/playbooks/car-connector-config.yml -vv --extra-vars '{"build_type":"upstream_relite_tag", "TRAVIS_BUILD_DIR":"'"${TRAVIS_BUILD_DIR}"'","TRAVIS_BUILD_NUMBER":"'"${TRAVIS_BUILD_NUMBER}"'", "TRAVIS_BRANCH":"'"${TRAVIS_BRANCH}"'", "COMMIT_ID":"'"${commit_id}"'"}' --vault-password-file vault_pass
    fi
else
# if we are in the fork
    echo "Running on fork with develop branch tasks"
    echo "Build Type: $build_type"
    ansible-playbook -i ./car-devops/inventory/develop ./car-devops/playbooks/car-connector-config.yml -vv --extra-vars '{"build_type":"'"${build_type}"'", "TRAVIS_BUILD_DIR":"'"${TRAVIS_BUILD_DIR}"'","TRAVIS_BUILD_NUMBER":"'"${TRAVIS_BUILD_NUMBER}"'", "TRAVIS_BRANCH":"develop", "COMMIT_ID":"'"${commit_id}"'", "RELEASE_VERSION":"'"${RELEASE_VERSION}"'"}' --vault-password-file vault_pass
fi
