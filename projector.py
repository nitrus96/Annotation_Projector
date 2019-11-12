import re
import pyconll
import collections

def project_annotations(path_to_src, path_to_tgt, alignment_file):
    # load from treebanks
    src = pyconll.load_from_file(path_to_src)
    tgt = pyconll.load_from_file(path_to_tgt)
    assert len(src) == len(tgt)
    # load the alignments
    algs = alg_generator(alignment_file)
    # iterate through treebanks
    for sent in range(len(src)):
        src_sent = src[sent]
        tgt_sent = tgt[sent]
        alg_sent = next(algs).split()
        src_to_tgt_dict = collections.defaultdict(list)
        tgt_to_src_dict = collections.defaultdict(list)
        # check that everything is properly formatted
        # and update alignment dictionaries
        for al in alg_sent:
            assert re.match(r'[0-9]*-[0-9]', al) is not None
            src_tok, tgt_tok = [int(i) + 1 for i in al.split('-')]
            # append the alignment dictionaries
            src_to_tgt_dict[src_tok].append(tgt_tok)
            tgt_to_src_dict[tgt_tok].append(src_tok)
            # iterate through the source sentence
            for tok in src_sent:
                s_i = int(tok.id)
                # check if token id is in the source dictionary (whether source -> target alignment exists)
                if s_i in src_to_tgt_dict.keys():
                    t_x = src_to_tgt_dict[s_i]
                # if not in source dictionary, the word is unaligned 
                else:
                    continue

                if len(t_x) == 1:
                    if t_x[0] == 1:
                        # one to one
                        pass
                    else:
                        # one to many
                        pass
                else:
                    for pos in t_x:
                        if len(pos) > 1:
                            # many to many
                            pass
                        # many to one
                        pass  

### SUPPORT FUNCTIONS ###

def swap_tgt_src(alg_file, output_file):
    with open(alg_file, 'r') as alg:
        alg = alg.readlines()
        with open(output_file, 'w') as alg_new:
            for line in alg:
                temp = re.findall(r"[0-9]*-[0-9]*", line)
                flipped = ' '.join([''.join([i.split('-')[1], '-', i.split('-')[0]]) for i in temp]) + '\n'
                alg_new.write(flipped)

def alg_generator(alignment_file):
    with open(alignment_file) as alg:
        for line in alg:
            yield line.rstrip('\n')

#project_annotations('./treebanks/new_uk_treebank.conllu', './treebanks/tokenized_be.conllu', './raw_data/uk_to_be.txt')


