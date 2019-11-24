import re
import pyconll
import collections
import codecs
from functools import wraps
from copy import copy
import re

def clean_token_ids(conllu, newfile):
    # load from treebanks
    conllu_file = pyconll.load_from_file(conllu)
    with codecs.open(newfile, 'a', "utf-8") as f:
        for sent in conllu_file:
            sent_str = sent.conll().split('\n')
            for token_line in sent_str:
                token_list = token_line.split('\t')
                
                # if line is a comment or token has a single number id, write
                if token_list[0].startswith('#') or ('-' not in token_list[0]):
                    f.write('\t'.join(token_list)+'\n')
            f.write('\n')

# specify paths to source treebank, target treebank, and alignment file
def project_annotations(path_to_src, path_to_tgt, alignment_file, save_file = 'proj_treebank.conllu'):
    # load from treebanks
    src = pyconll.load_from_file(path_to_src)
    tgt = pyconll.load_from_file(path_to_tgt)
    assert len(src) == len(tgt)
    # load the alignments
    algs = alg_generator(alignment_file)
    # iterate through treebank
    for sent in range(len(src)):
        save = True
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
        # make sure the sentence is properly aligned
        if max(src_to_tgt_dict.keys()) > len(src_sent) or max(tgt_to_src_dict.keys()) > len(tgt_sent):
            #print(max(src_to_tgt_dict), len(src_sent))
            #print("source to target:", src_to_tgt_dict)
            #print(max(tgt_to_src_dict), len(tgt_sent))
            print('Alignment in sentence {} is incorrect'.format(sent+1))
            continue

        # iterate through the source sentence
        for s_i in src_sent:
            if '-' not in s_i.id:
                s_i_id = int(s_i.id)
            else:
                continue
            # check that token id is in the source dictionary (whether source -> target alignment exists)
            if s_i_id in src_to_tgt_dict.keys():
                t_x = src_to_tgt_dict[s_i_id]
                if len(t_x) == 1:
                    t_x_id = t_x[0]
                    if len(tgt_to_src_dict[t_x_id]) == 1:
                        # one to one alignment
                        one_to_one(s_i, tgt_sent[t_x_id - 1], src_to_tgt_dict, src_sent, tgt_sent)
                    elif len(tgt_to_src_dict[t_x_id]) == 0:
                        continue
                    else:

                        # many to one alignment (not implemented)
                        # To-do: delete all alignments between source words and the target
                        # leave only the alignment between the head of source words and the target token
                        #print(src_to_tgt_dict[s_i_id])
                        #print(tgt_to_src_dict[s_i_id])
                        print('Many to one alignment in sentence {}, word id {}. Not implemented'.format(sent+1, s_i.id))
                        save = False
                        break

                else:
                    for pos in t_x:
                        if len(tgt_to_src_dict[pos]) > 1:
                            # many to many projection (not implemented)
                            print('Many to many alignment in sentence {}, word id {}. Not implemented'.format(sent+1, s_i.id))
                            save = False
                            break
                    # perform one to many alignment
                    #print("one to many for", s_i.form)
                    one_to_many(s_i, t_x, src_to_tgt_dict, src_sent, tgt_sent)

            # if not in the source dictionary, the word is unaligned 
            else:
                # check the word for any outgoing relations
                # if none exist, it can be ignored
                if s_i.id not in [word.head for word in src_sent]:
                    continue
                else:
                    print('There exists an unaligned word with an outgoing relation in sentence {}, word id {}. Not implemented'.format(sent+1, s_i.id))
                    save = False
                    break
        if save == True:
            save_to_file(save_file, tgt_sent)
        
### SUPPORT FUNCTIONS ###

def one_to_one(s_i, t_x, src_dict, src_sent, tgt_sent):
    # project upos tags 
    t_x.upos = s_i.upos
    # project dependencies
    t_x.deprel = s_i.deprel
    # project heads
    s_j = s_i.head
    # If token's head is not the root
    if s_j != str(0):
        try:
            t_x.head = str(src_dict[int(s_j)][0])
        # unaligned source head found
        # add dummy node
        except IndexError:
            print("unaligned source head found during 1:1")
            dummy = add_dummy(src_sent[s_j], src_dict, len(tgt_sent))
            tgt_sent._tokens.append(dummy)
            t_x.head = dummy.id
    else:
        t_x.head = str(0)

def one_to_many(s_i, t_x, src_dict, src_sent, tgt_sent):

    #print("T_X IS:", t_x)
    #print(src_sent.text)
    #print("source word:", s_i.form)
    try:
        dummy_pos = t_x[0]
        src_dict[int(s_i.id)] = [dummy_pos]
        tgt_sent[dummy_pos-1].upos = s_i.upos
        if s_i.head != str(0):
            try:
                tgt_sent[dummy_pos-1].head = str(src_dict[int(s_i.head)][0])
            except IndexError:
                tgt_sent[dummy_pos-1].head = str(0)
        tgt_sent[dummy_pos-1].deprel = s_i.deprel
        for pos in t_x[1:]:
            tgt_sent[pos-1].head = str(dummy_pos)
            tgt_sent[pos-1].deprel = 'dummy'
            tgt_sent[pos-1].upos = 'dummy'
    except IndexError:
        print("problem with t_x being an empty list")

def add_dummy(s_j, src_dict, tgt_sent_len):
    dummy = copy(s_j)
    dummy.id = str(tgt_sent_len+1)
    dummy._form = 'DUMMY'
    dummy.lemma = '_'
    dummy.deprel = s_j.deprel
    dummy.upos = s_j.upos
    dummy.feats = {}
    src_dict[int(s_j.id)].append(int(dummy.id))
    if s_j.head != str(0):
        try:
            dummy.head = str(src_dict[int(s_j.head)][0])
        except IndexError:
            dummy.head = str(0)
    return dummy    

def save_to_file(filename, sent):
    with codecs.open(filename, 'a', "utf-8") as f:
        words_to_keep = []
        shifts = []
        sent_by_line = sent.conll().split('\n')
        counter = iter(range(1, len(sent_by_line)+1))
        # go through each word
        for word in sent_by_line:
            # split word at tab
            tab_list = word.split("\t")
            # check that the word has no features/dependencies
            if tab_list.count('_') >= 6:
                shifts.append(tab_list[0])
                continue
            else:
                words_to_keep.append(tab_list)

        # fix word and head ids
        for word in words_to_keep:
            if not word[0].startswith('#'):
                word[0] = str(next(counter))
                #print(word)
                #print(word[6])
                if re.match(r"[0-9]", word[6]):
                    tgt_head = int(word[6])
                for shift in shifts:
                    if tgt_head >= int(shift):
                        word[6] = str(int(word[6]) - 1)
        f.write('\n'.join(['\t'.join(word) for word in words_to_keep]) + '\n\n')

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
 
 
#clean_token_ids("/home/shorouq/Desktop/rnd/fusha_ammani/data/MSA.conllu", "src_clean.conllu")
#clean_token_ids("/home/shorouq/Desktop/rnd/fusha_ammani/data/Amman.conllu", "tgt_clean.conllu")
#sent = project_annotations('./treebanks/new_uk_treebank.conllu', './treebanks/tokenized_be.conllu', './raw_data/uk_to_be.txt')
#sent = project_annotations('./test_sent/uk.conllu', './test_sent/be.conllu', './test_sent/alg.txt')
#sent = project_annotations('./one_to_many/one_to_many_uk.conllu', './one_to_many/one_to_many_be.conllu', './one_to_many/one_to_many_algs.txt')
#sent = project_annotations('/home/shorouq/Desktop/rnd/fusha_ammani/data/src_clean.conllu',
#'/home/shorouq/Desktop/rnd/fusha_ammani/data/tgt_clean.conllu', 
#'/home/shorouq/Desktop/rnd/fusha_ammani/data/src_tgt_forward.align')
sent = project_annotations("/home/shorouq/Desktop/rnd/fusha_ammani/data/georgie/src_parsed_500.conllu",
"/home/shorouq/Desktop/rnd/fusha_ammani/data/georgie/tgt_not_parsed_500.conllu", 
"/home/shorouq/Desktop/rnd/fusha_ammani/data/georgie/alignments500.txt") 