#! /usr/bin/env python

##############################################################################
##  DendroPy Phylogenetic Computing Library.
##
##  Copyright 2010 Jeet Sukumaran and Mark T. Holder.
##  All rights reserved.
##
##  See "LICENSE.txt" for terms and conditions of usage.
##
##  If you use this work or any portion thereof in published work,
##  please cite it as:
##
##     Sukumaran, J. and M. T. Holder. 2010. DendroPy: a Python library
##     for phylogenetic computing. Bioinformatics 26: 1569-1571.
##
##############################################################################

"""
Tests basic Tree structure and iteration.
"""

import unittest
import dendropy

###############################################################################
## Test Tree
# Following tree:
#
#                  a
#                 / \
#                /   \
#               /     \
#              /       \
#             /         \
#            /           \
#           /             c
#          b             / \
#         / \           /   \
#        /   e         /     f
#       /   / \       /     / \
#      /   /   \     g     /   h
#     /   /     \   / \   /   / \
#    i    j     k  l  m  n   o   p
#
#  Can be specified as:
#
#      a -> b -> i;
#      b -> e -> j;
#      e -> k;
#      a -> c;
#      c -> g;
#      c -> f;
#      g -> l;
#      g -> m;
#      f -> n;
#      f -> h -> o;
#      h -> p;
class TestTreeStructure(unittest.TestCase):
    dot_str = "a -> b -> i; b -> e -> j; e -> k; a -> c; c -> g; c -> f; g -> l; g -> m; f -> n; f -> h -> o; h -> p;"
    newick_unweighted_edges_str = "((i, (j, k)e)b, ((l, m)g, (n, (o, p)h)f)c)a;"
    newick_weighted_edges_str = "((i:1, (j:2, k:3)e:4)b:5, ((l:6, m:7)g:8, (n:9, (o:10, p:11)h:12)f:13)c:14)a:15;"
    preorder_sequence = ["a", "b", "i", "e", "j", "k", "c", "g", "l", "m", "f", "n", "h", "o", "p"]
    postorder_sequence = {"i", "j", "k", "e", "b", "l", "m", "g", "n", "o", "p", "h", "f", "c", "a"}
    leaf_sequence = {"i", "j", "k", "l", "m", "n", "o", "p"}
    level_order_sequence = {"a", "bc", "iegf", "jklmnh", "op"}
    internal_level_order_sequence = {"a", "bc", "egf", "h"}
    node_expected_children = {
            "a" : ["b", "c"],
            "b" : ["i", "e"],
            "c" : ["g", "f"],
            "e" : ["j", "k"],
            "f" : ["n", "h"],
            "g" : ["l", "m"],
            "h" : ["o", "p"],
            "i" : [],
            "j" : [],
            "k" : [],
            "l" : [],
            "m" : [],
            "n" : [],
            "o" : [],
            "p" : [],
            }
    node_expected_siblings = {
            "a": [],
            "b": ["c"],
            "c": [],
            "e": [],
            "f": [],
            "g": ["f"],
            "h": [],
            "i": ["e"],
            "j": ["k"],
            "k": [],
            "l": ["m"],
            "m": [],
            "n": ["h"],
            "o": ["p"],
            "p": [],
            }
    node_expected_edge_lengths = {
            "a": 15.0,
            "b":  5.0,
            "c": 14.0,
            "e":  4.0,
            "f": 13.0,
            "g":  8.0,
            "h": 12.0,
            "i":  1.0,
            "j":  2.0,
            "k":  3.0,
            "l":  6.0,
            "m":  7.0,
            "n":  9.0,
            "o": 10.0,
            "p": 11.0,
            }

    # def get_tree(self):
    #     tree = dendropy.Tree()
    #     def add_child_node(parent, label, edge_length):
    #         nd = tree.node_factory()
    #         nd.label = label
    #         nd.edge.length = edge_length
    #         parent.add_child(nd)
    #         return nd
    #     a = tree.seed_node
    #     a.label = "a"
    #     a.edge.length = 15.0
    #     b = add_child_node(a, label="b", edge_length=5.0)
    #     c = add_child_node(a, label="c", edge_length=14.0)
    #     e = add_child_node(b, label="i", edge_length=4.0)
    #     i = add_child_node(b, label="c", edge_length=1.0)
    #     j = add_child_node(e, label="j", edge_length=2.0)
    #     k = add_child_node(e, label="k", edge_length=3.0)
    #     f = add_child_node(c, label="f", edge_length=13.0)
    #     g = add_child_node(c, label="g", edge_length=8.0)
    #     l = add_child_node(g, label="l", edge_length=6.0)
    #     m = add_child_node(g, label="m", edge_length=7.0)
    #     h = add_child_node(f, label="h", edge_length=12.0)
    #     n = add_child_node(f, label="n", edge_length=9.0)
    #     o = add_child_node(h, label="o", edge_length=10.0)
    #     p = add_child_node(h, label="p", edge_length=11.0)
    #     return tree

    def get_tree(self):
        tree = dendropy.Tree()
        a = tree.seed_node
        a.label = "a"
        a.edge.length = 15.0
        b = a.new_child(label="b", edge_length=5.0)
        assert b.label == "b"
        assert b.edge.length == 5.0
        assert b.parent_node is a
        assert b.edge.tail_node is a
        assert b in a._child_nodes
        c = a.new_child(label="c", edge_length=14.0)
        assert c.label == "c"
        assert c.edge.length == 14.0
        assert c.parent_node is a
        assert c.edge.tail_node is a
        assert c in a._child_nodes
        e = b.new_child(label="e", edge_length=4.0)
        assert e.label == "e"
        assert e.edge.length == 4.0
        assert e.parent_node is b
        assert e.edge.tail_node is b
        assert e in b._child_nodes
        i = b.new_child(label="i", edge_length=1.0)
        assert i.label == "i"
        assert i.edge.length == 1.0
        assert i.parent_node is b
        assert i.edge.tail_node is b
        assert i in b._child_nodes
        j = e.new_child(label="j", edge_length=2.0)
        assert j.label == "j"
        assert j.edge.length == 2.0
        assert j.parent_node is e
        assert j.edge.tail_node is e
        assert j in e._child_nodes
        k = e.new_child(label="k", edge_length=3.0)
        assert k.label == "k"
        assert k.edge.length == 3.0
        assert k.parent_node is e
        assert k.edge.tail_node is e
        assert k in e._child_nodes
        f = c.new_child(label="f", edge_length=13.0)
        assert f.label == "f"
        assert f.edge.length == 13.0
        assert f.parent_node is c
        assert f.edge.tail_node is c
        assert f in c._child_nodes
        g = c.new_child(label="g", edge_length=8.0)
        assert g.label == "g"
        assert g.edge.length == 8.0
        assert g.parent_node is c
        assert g.edge.tail_node is c
        assert g in c._child_nodes
        l = g.new_child(label="l", edge_length=6.0)
        assert l.label == "l"
        assert l.edge.length == 6.0
        assert l.parent_node is g
        assert l.edge.tail_node is g
        assert l in g._child_nodes
        m = g.new_child(label="m", edge_length=7.0)
        assert m.label == "m"
        assert m.edge.length == 7.0
        assert m.parent_node is g
        assert m.edge.tail_node is g
        assert m in g._child_nodes
        h = f.new_child(label="h", edge_length=12.0)
        assert h.label == "h"
        assert h.edge.length == 12.0
        assert h.parent_node is f
        assert h.edge.tail_node is f
        assert h in f._child_nodes
        n = f.new_child(label="n", edge_length=9.0)
        assert n.label == "n"
        assert n.edge.length == 9.0
        assert n.parent_node is f
        assert n.edge.tail_node is f
        assert n in f._child_nodes
        o = h.new_child(label="o", edge_length=10.0)
        assert o.label == "o"
        assert o.edge.length == 10.0
        assert o.parent_node is h
        assert o.edge.tail_node is h
        assert o in h._child_nodes
        p = h.new_child(label="p", edge_length=11.0)
        assert p.label == "p"
        assert p.edge.length == 11.0
        assert p.parent_node is h
        assert p.edge.tail_node is h
        assert p in h._child_nodes
        tree.debug_check_tree()
        leaf_nodes = set([i, j, k, l, m, n, o, p])
        internal_nodes = set([b, c, e, f, g, h])
        all_nodes = leaf_nodes | internal_nodes | set([a])
        return tree, all_nodes, leaf_nodes, internal_nodes

    def test_get_nodes(self):
        tree, anodes, lnodes, inodes = self.get_tree()
        nodes = tree.nodes()
        self.assertEqual(len(nodes), len(anodes))
        self.assertEqual(set(nodes), anodes)


if __name__ == "__main__":
    unittest.main()