#!/bin/bash

set -xe

# build
PROJECT=$(basename $(dirname $(realpath $0)))
DIRECTORY=/opt/webeye/${PROJECT}
echo ${PROJECT}
cd $(dirname $(realpath $0))

# changelog
git log --oneline --pretty=format:"%h %s" -5 | tee CHANGELOG

# deploy
SSH="ssh -F ssh_config"
IP_LIST=$(echo  ${IP}| sed  's/,/ /g')
for IP in ${IP_LIST}
do
	IP=$(echo ${IP} | egrep -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
	case ${IP} in
	    35.187.243.180 )
	        ENV=production-us
	        ;;
	    35.241.122.221 )
	        ENV=production-us
	        ;;
	    47.100.247.92 )
	        ENV=production-cn
	        ;;
	    35.241.103.229 )
	        ENV=development
	        ;;
	    * )
	        ENV=development
	        ;;
	esac
	echo IP=${IP}, ENV=${ENV}
	${SSH} ${IP} "sudo mkdir -p ${DIRECTORY}/logs"
	${SSH} ${IP} "sudo chown -R \"\$(whoami)\" ${DIRECTORY}"
	rsync -e "${SSH}" -avz --chmod=o-w --exclude-from='rsync-excludes.txt' . ${IP}:${DIRECTORY}/
	${SSH} ${IP} "cd ${DIRECTORY} && env PIPENV_VENV_IN_PROJECT=1 pipenv run pip install pip==18.0"
	${SSH} ${IP} "cd ${DIRECTORY} && env PIPENV_VENV_IN_PROJECT=1 pipenv install"
	${SSH} ${IP} "echo ENV=${ENV} | sudo tee ${DIRECTORY}/.env"
	${SSH} ${IP} "cd ${DIRECTORY} && sudo systemctl reload-or-restart ${PROJECT}"
	${SSH} ${IP} "cd ${DIRECTORY} && sudo nginx -t && sudo nginx -s reload"
done

rm -f CHANGELOG
