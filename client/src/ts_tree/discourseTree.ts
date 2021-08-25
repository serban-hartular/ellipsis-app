import type ConlluTree from "./tree"

export default class DiscourseTree {
    content : ConlluTree = null
    left : DiscourseTree
    right : DiscourseTree
    type : string = ''
    component_text : string = ''
    parent : DiscourseTree
    constructor(tree : ConlluTree, parent : DiscourseTree = null) {
        if(this.separateCoordinateClause(tree))
            return
        if(this.separateRelativeClause(tree))
            return
        if(this.separateSConjClause(tree))
            return
        this.content = tree
        this.left = null
        this.right = null
        this.component_text = tree.component_text
        this.parent = parent
    }
    c_commands_me() : Array<DiscourseTree> {
        let c_commanders : Array<DiscourseTree> = []
        let node : DiscourseTree = this
        while(node.parent) {
            let parent = node.parent
            c_commanders.push(node == parent.left ? parent.right : parent.left)
            node = parent
        }
        return c_commanders
    }
    content_matches(dict : Object) : boolean {
        
        return this.content && this.content.find(dict) != null
    }
    separateCoordinateClause(tree:ConlluTree) : boolean {
        let conjs = tree.childrenMatch({'DEPREL':'conj'}) // conjunct tree
        if(!conjs)
            return false
        this.component_text = tree.component_text
        let conj = conjs.pop()
        tree.removeChild(conj)
        let cc = conj.childMatches({'DEPREL':'cc'}) //coordinate conjunction
        if(cc) {
            conj.removeChild(cc)
            this.content = cc
        }
        this.left = new DiscourseTree(tree, this)
        this.right = new DiscourseTree(conj, this)
        this.type = 'symmetric'
        return true
    }
    separateRelativeClause(tree:ConlluTree) : boolean {
        //this first part is ugly, redo it later
        let ccomp = tree.childrenMatch({'DEPREL':'ccomp'}); if(!ccomp) ccomp = [] 
        let advcl = tree.childrenMatch({'DEPREL':'advcl'}); if(!advcl) advcl = []
        let xcomp = tree.childrenMatch({'DEPREL':'xcomp'}); if(!xcomp) xcomp = [] 
        let rels = ccomp.concat(advcl); rels = rels.concat(xcomp)
        // console.log(tree.childrenMatch({'DEPREL':'advcl'}))
        // console.log(rels)
        // console.log(rels[0].childMatches({'PronType':'Rel'}))
        rels = rels.filter(n => n.childMatches({'PronType':'Rel'}) != null) //filter for Relative Pron/Adv
        if(rels.length == 0)
            return false
        let rel = rels[0]
        this.component_text = tree.component_text
        tree.removeChild(rel)
        let rel_pron = rel.childMatches({'PronType':'Rel'}) //relative pron/adv
        rel.removeChild(rel_pron)
        this.content = rel_pron
        this.left = new DiscourseTree(tree, this)
        this.right = new DiscourseTree(rel, this)
        this.type = 'relative'
        return true
    }
    separateSConjClause(tree:ConlluTree) : boolean { //subordinate via conjunction
        //this first part is ugly, redo it later
        let ccomp = tree.childrenMatch({'DEPREL':'ccomp'}); if(!ccomp) ccomp = [] 
        let advcl = tree.childrenMatch({'DEPREL':'advcl'}); if(!advcl) advcl = []
        let xcomp = tree.childrenMatch({'DEPREL':'xcomp'}); if(!xcomp) xcomp = [] 
        let subs = ccomp.concat(advcl); subs = subs.concat(xcomp)
        subs = subs.filter(n => n.childMatches({'DEPREL':'mark'}) != null &&
            !['să', 'că'].includes(n.childMatches({'DEPREL':'mark'}).component_text.trim().toLowerCase()) ) //filter for Relative Pron/Adv
        if(subs.length == 0)
            return false
        let sub = subs[0]
        this.component_text = tree.component_text
        tree.removeChild(sub)
        let sconj = sub.childMatches({'DEPREL':'mark'}) //relative pron/adv
        sub.removeChild(sconj)
        this.content = sconj
        this.left = new DiscourseTree(tree, this)
        this.right = new DiscourseTree(sub, this)
        this.type = 'asymmetric'
        return true
    }
    isLeaf() : boolean { return this.left == null && this.right == null }
}