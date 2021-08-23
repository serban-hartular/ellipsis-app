
from cube.api import Cube
# #from cube.io_utils.conll import ConllEntry
# 
# cube_ro=Cube(verbose=True)         # initialize it
# cube_ro.load("ro")                 # select the desired language (it will auto-download the model on first run)
# 
# cube_en = Cube(verbose=True)
# cube_en.load("en")

conll_entry_attribs = ['index', 'word', 'lemma', 'upos', 'xpos', 'attrs', 'head', 'label', 'deps', 'space_after']
conll_field_dict = {'index':'ID', 'word':'FORM', 'lemma':'LEMMA', 'upos':'UPOS', 'xpos':'XPOS',
                    'attrs':'FEATS', 'head':'HEAD', 'label':'DEPREL', 'deps':'DEPS', 'space_after':'MISC'}

CHILDREN = 'children'
TREE_FORM = 'TREE_FORM'

def conll_entry_to_dict(entry) -> dict:
    d = dict()
    for attrib in conll_entry_attribs:
        # d[conll_field_dict[attrib]] = entry.__getattribute__(attrib)
        d[conll_field_dict[attrib]] = str(entry.__getattribute__(attrib))
    d[CHILDREN] = list()
    return d

def add_tree_form(tree : dict):
    for child in tree[CHILDREN]:
        add_tree_form(child)
    forms = [child for child in tree[CHILDREN]]
    forms.append(tree)
    forms.sort(key=lambda n : float(n['ID']))
    tree_form = ''
    for f in forms: # not pythonic, but more legible
        if f == tree:
            tree_form += f['FORM']
            if 'SpaceAfter=No' not in f['MISC']:
                tree_form += ' '
        else:
            tree_form += f[TREE_FORM]
    tree[TREE_FORM] = tree_form

def text_to_treelist(text : str, cube : Cube, OLD_API = False) -> list:
    """Given a text, returns a list of parse trees, one for each sentence in the text.
    Each parse tree is in the form of a dict with k,v pairs for the 10 conllu parameters
    (ID, FORM, LEMMA, UPOS, etc.), plus a key 'children' whose value is a list of dicts
    containing the node's children."""
    if OLD_API:
        sentences = cube(text)
    else:
        doc = cube(text)
        sentences = doc.sentences # this is needed because new API, dammit!
    treelist = []
    for sentence in sentences:
        sentence = [conll_entry_to_dict(entry) for entry in (sentence if OLD_API else sentence.words)]
        # sentence = [conll_entry_to_dict(entry) for entry in sentence.words]
        # now build tree
        tree = [w for w in sentence] # first, just copy the words
        for word in sentence: # for each word
            # find its head, ie parent
            head = [h for h in sentence if h['ID'] == word['HEAD']]
            if len(head) == 1:
                head = head[0]
                head[CHILDREN].append(word)
                tree.remove(word) # if have found head, remove from list
        if len(tree) == 1: # list should have only 1 item, the root
            treelist.append(tree[0])
            # add_tree_form(tree[0])
    return treelist
