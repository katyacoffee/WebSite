#!/bin/sh

DIR_PROG=`dirname $0`
FILE_PROG=`basename $0`

DIR_FUNC="$HOME/bin/sh_func"

. $DIR_FUNC/f_begin.sh_func
. $DIR_FUNC/f_dir_test.sh_func

DIR_DATA="DATA"

FILE_PROG_VLF2CSV="$HOME/bin/METRONIX/MATLAB/SDV/VLF2CSV/run_vlf2csv.sh /usr/local/MATLAB/MATLAB_Runtime/v95"

$FILE_PROG_VLF2CSV $DIR_DATA/

. $DIR_FUNC/f_end.sh_func

exit 0


DIR_DATA="/DATA/DATA_MIKHNEVO/GNSS/Javad_Sigma"
DIR_INOUT_IN_RINEX2MAT="$DIR_PROG/../INOUT/02-03"
DIR_INOUT_OUT_GET_TECV_FROM_MATLAB_IR="$DIR_PROG/../INOUT/03-04"
DIR_DATA_MAT="$DIR_DATA/03_RINEX_MAT"

FILE_MASK_O="*.*o"

FILE_PROG_RINEX2MAT="$HOME/bin/GNSS/MATLAB/matlab_rinex2mat/run_Rinex2mat.sh /usr/local/MATLAB/MATLAB_Runtime/v95"

for i in `ls $DIR_INOUT_IN_RINEX2MAT/$FILE_MASK_O 2> /dev/null ` ; do
    file_name=`basename $i | awk -F "." '{print $1}'`
    year=`echo $file_name | awk -F "_" '{print $2}'`
    dir_test $DIR_DATA_MAT/$year
    $FILE_PROG_RINEX2MAT $i $DIR_DATA_MAT/$year/
    cp -v $DIR_DATA_MAT/$year/${file_name}.mat $DIR_INOUT_OUT_GET_TECV_FROM_MATLAB_IR
    rm -v $DIR_INOUT_IN_RINEX2MAT/${file_name}.*
done

. $DIR_FUNC/f_end.sh_func

exit 0

