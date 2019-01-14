pid_file='/opt/syncDirectory/pid'
log_file='/opt/syncDirectory/log'
name='Sync Directory'

start() {
 	pid=$(cat $pid_file)

	if ! kill -0 $pid > /dev/null 2>&1; then
		echo $name "has started."
        python "/opt/syncDirectory/syncd.py" &> $log & echo $! > $pid_file
	else
		echo $name "is running now."
	fi
}

stop() {
	cpid=$(cat $pid_file)
	ppid=$(pgrep -P $cpid)

	if kill -0 $cpid > /dev/null 2>&1; then
		kill $ppid
		kill $cpid
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
