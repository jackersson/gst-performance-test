

N=1
RTSP=false
while :; do
    case $1 in
        -n|--number) 
            shift
            N=$1  
            echo "Count = $N"        
        ;;
        --rtsp) 
            RTSP=true  
            echo $RTSP         
        ;;
        *) break
    esac
    shift
done

# fdate=$(date '+%d-%m-%Y');
# ftime=$(date '+%H-%M-%S')

exec > >(tee log/$N.log)

if $RTSP
then
    GST_DEBUG=python3:1 python3 run.py -n $N --rtsp
else
    GST_DEBUG=python3:1 python3 run.py -n $N --file
fi
