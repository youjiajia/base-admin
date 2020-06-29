#!/bin/bash

SRC_DIR_NAME=admin
APP_NAME=admin-login
DEST_DIR=/opt/webeye/$APP_NAME/
SSH_USER=bidev
SSH_HOST=35.241.103.229
SSH_ALIAS=bidev-test


if [ $(basename "$PWD") == "deploy" ]; then
    cd ..
fi

if [ $(basename "$PWD") != $SRC_DIR_NAME ]; then
    echo "please run in project root or deploy folder"
    exit 1
fi


RESTART=y

while [[ $# -gt 0 ]]; do    # As long as there is at least one more argument, keep looping
    key="$1"
    case "$key" in
        -n|--no-restart)       # Also a flag type option. Will catch either -b or --bar
        RESTART=n
        ;;
        -h|--help)
        echo "-n/--no-restart"
        exit 1
        ;;
        *)
        echo "unknown option '$key', -n/--no-restart" # Do whatever you want with extra options
        exit 1
        ;;
    esac
    shift                           # Shift after checking all the cases to get the next option
done
echo "restart: $RESTART"

echo "generate COMMIT_POINT file...."
git log -1 > COMMIT_POINT


echo "begin to rsync files...."
#rsync -avzh --delete --exclude-from=rsync-excludes.txt * $SSH_USER@$SSH_HOST:$DEST_DIR
rsync -avzh --delete --exclude-from=rsync-excludes.txt * $SSH_ALIAS:$DEST_DIR

rm COMMIT_POINT


if [ "$RESTART" == "y" ]; then
    echo "rsync done, begin to restart app...."
    #ssh $SSH_USER@$SSH_HOST "cd $DEST_DIR;pipenv run supervisorctl restart $APP_NAME:*"
    ssh $SSH_ALIAS "cd $DEST_DIR;pipenv run supervisorctl restart $APP_NAME:*"
fi

echo "all done !!!"
