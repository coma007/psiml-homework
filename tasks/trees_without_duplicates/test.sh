DIR="public/inputs"
NUM_FILES=$(ls -1 "$DIR" | wc -l)

FAILS=0

for (( var=1; var<=$NUM_FILES; var++ ))
do
    test=""
    
    if (( var<10 ))
    then
        test="0$var"
    else
        test="$var"
    fi

    input="public/inputs/$test.txt"
    output="public/outputs/$test.txt"
    result="public/results/$test.txt"

    python3 solution.py < "$input" > "$result"
    if diff -q "$result" "$output" --ignore-all-space; then
        echo "Test $test : SUCCESS"
    else
        echo "Test $test : FAIL"
        FAILS=$(( FAILS + 1 ))
    fi
done

SUCCESS_RATE=$(( (NUM_FILES-FAILS)*100 / NUM_FILES ))
echo "------------------"
echo "Success rate: $SUCCESS_RATE%"