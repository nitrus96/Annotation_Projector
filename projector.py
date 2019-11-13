import re
import pyconll
import collections
import codecs

def project_annotations(path_to_src, path_to_tgt, alignment_file):
    # load from treebanks
    src = pyconll.load_from_file(path_to_src)
    tgt = pyconll.load_from_file(path_to_tgt)
    assert len(src) == len(tgt)
    # load the alignments
    algs = alg_generator(alignment_file)
    # iterate through treebank
    for sent in range(len(src)):
        src_sent = src[sent]
        tgt_sent = tgt[sent]
        alg_sent = next(algs).split()
        src_to_tgt_dict = collections.defaultdict(list)
        tgt_to_src_dict = collections.defaultdict(list)
        # check that everything is properly formatted
        # and update alignment dictionaries
        for al in alg_sent:
            assert re.match(r'[0-9]+-[0-9]+', al) is not None
            src_tok, tgt_tok = [int(i) + 1 for i in al.split('-')]
            # append the alignment dictionaries
            src_to_tgt_dict[src_tok].append(tgt_tok)
            tgt_to_src_dict[tgt_tok].append(src_tok)
            # iterate through the source sentence
        for s_i in src_sent:
            s_i_id = int(s_i.id)
            # check if token id is in the source dictionary (whether source -> target alignment exists)
            if s_i_id in src_to_tgt_dict.keys():
                t_x = src_to_tgt_dict[s_i_id]
                if len(t_x) == 1:
                    t_x_id = t_x[0]
                    if len(tgt_to_src_dict[t_x_id]) == 1:
                        # one to one
                        one_to_one(s_i, tgt_sent[t_x_id - 1], src_to_tgt_dict)
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
            # if not in the source dictionary, the word is unaligned 
            else:
                # check the word for any outgoing relations
                if s_i.id not in [word.head for word in src_sent]:
                    print('There is an unaligned word but we can ignore it in sentence {}'.format(sent+1))
                    continue
                else:
                    print('There exists an unaligned word with an outgoing relation in sentence {}'.format(sent+1))
        save_to_file('trial.conllu', tgt_sent)

    ## NB we can just save the modified treebank once everything is projected ##

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

def one_to_one(s_i, t_x, src_dict):
    # project upos tags 
    t_x.upos = s_i.upos
    # project dependencies
    t_x.deprel = s_i.deprel
    # project heads
    s_j = s_i.head
    if s_j != str(0):
        t_x.head = str(src_dict[int(s_j)][0])
    else:
        t_x.head = str(0)

def save_to_file(filename, sent):
    with codecs.open(filename, 'a', "utf-8") as f:
        f.write(sent.conll() + '\n\n')




sent = project_annotations('./treebanks/new_uk_treebank.conllu', './treebanks/tokenized_be.conllu', './raw_data/uk_to_be.txt')


