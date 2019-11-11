import re
import pyconll
import collections

def swap_tgt_src(alg_file, output_file):
    with open(alg_file, 'r') as alg:
        alg = alg.readlines()
        with open(output_file, 'w') as alg_new:
            for line in alg:
                temp = re.findall(r"[0-9]*-[0-9]*", line)
                flipped = ' '.join([''.join([i.split('-')[1], '-', i.split('-')[0]]) for i in temp]) + '\n'
                alg_new.write(flipped)

def project_annotations(path_to_src, path_to_tgt, alignment_file):
    # load from treebanks
    src = pyconll.load_from_file(path_to_src)
    tgt = pyconll.load_from_file(path_to_tgt)
    # load the alignment file
    with open(alignment_file, 'r') as alg:
        alg = alg.readlines()
    assert len(src) == len(tgt) and len(src) == len(alg)
    # iterate through treebanks
    for sent in range(len(src)):
        src_sent = src[sent]
        tgt_sent = tgt[sent]
        alg_sent = alg[sent].rstrip('\n').split()
        src_to_tgt_dict = collections.defaultdict(list)
        tgt_to_src_dict = collections.defaultdict(list)
        # check that everything is properly formatted
        # and update alignment dictionary 
        for al in alg_sent:
            assert re.match(r'[0-9]*-[0-9]', al) is not None
            src_tok, tgt_tok = [int(i) for i in al.split('-')]
            # append the alignment dictionaries
            src_to_tgt_dict[src_tok].append(tgt_tok)
            tgt_to_src_dict[tgt_tok].append(src_tok)


        # iterate through each source sentence
        for tok in range(0, len(tgt_sent)):
            # one-to-one alignment
            s_i = tok.id
            
            # unaligned source
        
src, tgt = project_annotations('./treebanks/new_uk_treebank.conllu', './treebanks/tokenized_be.conllu')

