import re
import pyconll

def swap_tgt_src(alg_file, output_file):
    with open(alg_file, 'r') as alg:
        alg = alg.readlines()
        with open(output_file, 'w') as alg_new:
            for line in alg:
                temp = re.findall(r"[0-9]*-[0-9]*", line)
                flipped = ' '.join([''.join([i.split('-')[1], '-', i.split('-')[0]]) for i in temp]) + '\n'
                alg_new.write(flipped)
                



