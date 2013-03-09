
INPUT_DIR=inputs
OUTPUT_DIR=results
INPUT_FILES='stag_prob_0_2_3_data'

for f in $INPUT_FILES;
do
	input_file=$INPUT_DIR/$f	
	out_dir=$OUTPUT_DIR/$f
        sudo python hedera.py -i $input_file -d $out_dir -n
done
