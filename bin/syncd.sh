#!/bin/sh
path=/opt/syncd
pid_file=$path/pid
log_file=$path/log
name='Sync Directory'

start() {
 	pid=$(cat $pid_file)

	if ! kill -0 $pid 2> /dev/null; then
		echo $name "has started."
        	python $path/syncd.py &> $log_file & echo $! > $pid_file
	else
		echo $name "is running now."
	fi
}

stop() {
	cpid=$(cat $pid_file)

	if kill -0 $cpid 2> /dev/null; then
		kill $cpid > /dev/null
		echo $name "has stopped."
	else
		echo "Is not running."
	fi
}

if [ "$1" = "start" ]
then
    start
fi

if [ "$1" = "stop" ]
then
    stop
fi

exit 0
