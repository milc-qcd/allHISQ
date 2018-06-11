# CD modified usage:
#  cd_launcher <exec> <exec_args>

lrank=$(($PMIX_RANK % 6))
export OMP_NUM_THREADS=7 
case ${lrank} in
[0])
export PAMI_IBV_DEVICE_NAME=mlx5_0:1
numactl --physcpubind=0,4,8,12,16,20,24 --membind=0 $*
  ;;

[1])
export PAMI_IBV_DEVICE_NAME=mlx5_0:1
numactl --physcpubind=28,32,36,40,44,48,52 --membind=0 $*
  ;;

[2])
export PAMI_IBV_DEVICE_NAME=mlx5_0:1
numactl --physcpubind=56,60,64,68,72,76,80 --membind=0 $*
  ;;

[5])
export PAMI_IBV_DEVICE_NAME=mlx5_3:1
numactl --physcpubind=88,92,96,100,104,108,112 --membind=8 $*
  ;;

[3])
export PAMI_IBV_DEVICE_NAME=mlx5_3:1
numactl --physcpubind=116,120,124,128,132,136,140 --membind=8 $*
  ;;

[4])
export PAMI_IBV_DEVICE_NAME=mlx5_3:1
numactl --physcpubind=144,148,152,156,160,164,168 --membind=8 $*
  ;;
esac
