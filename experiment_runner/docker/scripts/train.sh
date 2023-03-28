command_exists () {
    type "$1" &> /dev/null ;
}

DEVICE=cpu

if command_exists nvidia-smi ; then
    DEVICE=gpu
fi

echo USING DEVICE: $DEVICE

docker-compose -f docker-compose.$DEVICE.yml up $*
