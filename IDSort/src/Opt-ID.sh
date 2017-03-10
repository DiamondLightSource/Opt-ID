echo "Hostname is "
echo $HOSTNAME

. /etc/profile.d/modules.sh
module load python/ana
which python
echo python /home/ssg37927/ID/Opt-ID/IDSort/src/v2/Opt-ID.py $@ 
time python /home/ssg37927/ID/Opt-ID/IDSort/src/v2/Opt-ID.py $@ 
