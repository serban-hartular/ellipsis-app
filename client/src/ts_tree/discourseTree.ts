import type ConlluTree from "./tree"

export class DiscourseTree {
    content : ConlluTree = null
    left : DiscourseTree
    right : DiscourseTree
    constructor(tree : ConlluTree) {
        if(this.separateCoordinateClauses(tree))
            return
        this.content = tree
        this.left = null
        this.right = null
    }
    separateCoordinateClauses(tree:ConlluTree) : boolean {
        let conj = tree.childMatches({'DEPREL':'conj'}) // conjunct tree
        if(!conj)
            return false
        tree.removeChild(conj)
        let cc = conj.childMatches({'DEPREL':'cc'}) //coordinate conjunction
        if(cc) {
            conj.removeChild(cc)
            this.content = cc
        }
        this.left = new DiscourseTree(tree)
        this.right = new DiscourseTree(conj)
        return true
    }
    isLeaf() : boolean { return this.left == null && this.right == null }
}