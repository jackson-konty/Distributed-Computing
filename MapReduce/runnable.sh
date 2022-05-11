
while :
do
echo "1. Custom test with interface"
echo "2. Custom test with configure file"
echo "3. Default word count test"
echo "4. Default inverted index test"
echo -n "Type 1 or 2 or 3 or 4: "
read -n 1 -t 15 a
printf "\n"
case $a in
1* )     py interface.py; break;;

2* )     py configure.py; break;;
 
3* )     py test1.py; break;;
 
4* )     py test2.py; break;;

 
* )     echo "Try again.";;
esac
done