#!/bin/bash

SRC_DIR_NAME=admin
APP_NAME=admin-login
DEST_DIR=/opt/webeye/$APP_NAME/
SSH_USER=bidev
SSH_HOST="admin-login"


if [ $(basename "$PWD") == "deploy" ]; then
    cd ..
fi

if [ $(basename "$PWD") != $SRC_DIR_NAME ]; then
    echo "please run in project root or deploy folder"
    exit 1
fi


RESTART=y
BUILD_UI=n

while [[ $# -gt 0 ]]; do    # As long as there is at least one more argument, keep looping
    key="$1"
    case "$key" in
        --build-ui)      # This is a flag type option. Will catch either -f or --foo
        BUILD_UI=y
        ;;
        -n|--no-restart)       # Also a flag type option. Will catch either -b or --bar
        RESTART=n
        ;;
        -h|--help)
        echo "-n/--no-restart"
        exit 1
        ;;
        *)
        echo "unknown option '$key', --build-ui -n/--no-restart" # Do whatever you want with extra options
        exit 1
        ;;
    esac
    shift                           # Shift after checking all the cases to get the next option
done

echo "build-ui: $BUILD_UI"
echo "restart: $RESTART"

read -p "Are you sure to update production server with above options? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

echo "generate COMMIT_POINT file...."
git log -1 > COMMIT_POINT


if [ "$BUILD_UI" == "y" ]; then
   ./build_ui.sh
fi


echo "begin to rsync files...."
for host in $SSH_HOST; do
    echo "sync $host"
    rsync -avzh --delete --exclude-from=rsync-excludes.txt * $SSH_USER@$host:$DEST_DIR
done

rm COMMIT_POINT


if [ "$RESTART" == "y" ]; then
    echo "rsync done, begin to restart app...."
    for host in $SSH_HOST; do
        echo "restart $host"
        ssh $SSH_USER@$host "cd $DEST_DIR;pipenv run supervisorctl restart $APP_NAME:*"
    done
fi

echo "all done !!!"
