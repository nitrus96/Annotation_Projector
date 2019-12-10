# Annotation_Projector

A tool to facilitate transfer of morphosyntactic information between Universal Dependencies treebanks.

The main function `project_annotations` accepts the following arguments:
* `path_to_src`, `path_to_tgt`: paths to source and target treebanks (must be in conllu format)
* `alignment_file`: path to the alignment file (in the 'Pharaoh' format like 0-0 1-1 2-3 3-2, with indexing starting at 0 and sentence boundaries demarkated by a new line)

Helper functions `swap_tgt_src` and `clean_token_ids` swap the alignment direction and clean up multiword token ids respectively. 

