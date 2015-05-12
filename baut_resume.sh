#!/bin/bash

work_dir=$1

mkdir -p $work_dir/results
rm -r $work_dir/results/* 2> /dev/null

#creating results dirs
for dir in $work_dir/tests/*; do
	if [[ -z $(ls $dir) ]]; then
		echo "[resume.sh] skipping empty dir '$dir' ..."
		continue
	fi

	echo "[resume.sh] working in $dir ..."

	final_line_start=$(basename $dir)

	for subdir in $dir/*; do
		app_name=$(basename $subdir)
		mkdir -p $work_dir/results/$app_name
		final_line=$final_line_start

		for (( i=1; i<=3; i+=1 )); do
			line=$(cat $subdir/time_results.txt | head -n $i | tail -n 1 | sed s/:/,/g | sed s/\ //g)
			avg=$(echo $line | cut -f3 -d",")
			ci=$(echo $line | cut -f5 -d",")
			case $i in
				1 )
					real_avg=$avg ;;
				2 )
					user_avg=$avg ;;
				3 )
					sys_avg=$avg ;;	
			esac
			final_line+=",$avg,$ci"
		done

		final_line+=",$(printf "%.3f" $(echo "($user_avg + $sys_avg) / $real_avg" | bc -l))"

		echo $final_line >> $work_dir/results/$app_name/time_results.csv
	done
done

echo "[resume.sh] sorting ..."

#sorting
for app_name in $work_dir/results/*; do
	cat $app_name/time_results.csv | sort -k2n --field-separator=, > $app_name/time_results_sorted.csv
	mv $app_name/time_results_sorted.csv $app_name/time_results.csv
	cp $app_name/time_results.csv $app_name/time_results_no_header.csv
	sed -i -e '1iTYPE,REAL_AVG_SECS,REAL_CI,USER_AVG_SECS,USER_CI,SYS_AVG_SECS,SYS_CI,(USER_AVG_SECS+SYS_AVG_SECS)/REAL_AVG_SECS\' $app_name/time_results.csv
done

#making csv file
echo "[resume.sh] making final resume file ..."
echo "APPLICATION,TYPE,REAL_AVG,REAL_CI,USER_AVG,USER_CI,SYS_AVG,SYS_CI,(USER_AVG+SYS_AVG)/REAL_AVG" > $work_dir/final_resume.csv
for dir in $work_dir/results/*; do
	app=$( echo $dir | rev | cut -f1 -d"/" | rev )
	while read line; do
		echo "$app,$line" >> $work_dir/final_resume.csv 
	done < $dir/time_results_no_header.csv
done

echo "[resume.sh] done."
