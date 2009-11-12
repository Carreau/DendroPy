#! /usr/bin/env python

###############################################################################
##  DendroPy Phylogenetic Computing Library.
##
##  Copyright 2009 Jeet Sukumaran and Mark T. Holder.
##
##  This program is free software; you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation; either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License along
##  with this program. If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################

"""
Functions and classes for manipulating or changing tree
structural relations.
"""

import sys
import copy
import math

from dendropy.utility import GLOBAL_RNG
from dendropy import splitmask
from dendropy import dataobject

def collapse_edge(edge):
    '''Inserts all children of the head_node of edge as children of the
    tail_node of edge in the same place in the child_node list that head_node
    had occupied.

    The edge length and head_node will no longer be part of the tree.'''
    to_del = edge.head_node
    p = edge.tail_node
    if not p:
        return
    children = to_del.child_nodes()
    if not children:
        raise ValueError('collapse_edge called with a terminal.')
    pos = p.child_nodes().index(to_del)
    p.remove_child(to_del)
    for child in children:
        p.add_child(child, pos=pos)
        pos += 1

def collapse_clade(node):
    """Collapses all internal edges that are descendants of node."""
    if node.is_leaf():
        return
    leaves = [i for i in dataobject.Node.leaf_iter(node)]
    node.set_children(leaves)

def prune_taxa(tree, taxon_set):
    """Removes terminal edges associated with taxa in `taxa` from `tree`."""
    for taxon in taxon_set:
        nd = tree.find_node(lambda x: x.taxon == taxon)
        if nd is not None:
            nd.edge.tail_node.remove_child(nd)
    # clean up dead leaves
    for nd in tree.postorder_node_iter():
        if nd.taxon is None and len(nd.child_nodes()) == 0:
            dnd = nd
            while dnd.taxon is None and dnd.parent_node is not None and len(dnd.child_nodes()) == 0:
                new_dnd = dnd.parent_node
                new_dnd.remove_child(dnd)
                dnd = new_dnd
    # remove outdegree 1 nodes
    for nd in tree.postorder_node_iter():
        children = nd.child_nodes()
        if nd.parent_node is not None and len(children) == 1:
            nd.parent_node.add_child(children[0])
            if nd.edge.length is not None:
                if children[0].edge.length is None:
                    children[0].edge.length = nd.edge.length
                else:
                    children[0].edge.length += nd.edge.length
            nd.parent_node.remove_child(nd)
    return tree

def retain_taxa(tree, taxa):
    """Removes all taxa *not* in `taxa` from the tree."""
    to_prune = [t for t in tree.taxon_set if t not in taxon_set]
    return prune_taxa(tree, to_prune)

def randomly_reorient_tree(tree, rng=None, splits=False):
    """Randomly picks a new rooting position and rotates the branches around all
    internal nodes in the `tree`.

    If `splits` is True, the the `clade_mask` and `split_edges` attributes
        kept valid.
    """
    nd = rng.sample(tree.nodes(), 1)[0]
    if nd.is_leaf():
        tree.to_outgroup_position(nd, splits=splits)
    else:
        tree.reroot_at(nd, splits=splits)
    randomly_rotate(tree, rng=rng)

def randomly_rotate(tree, rng=None):
    "Randomly rotates the branches around all internal nodes in the `tree`"
    if rng is None:
        rng = GLOBAL_RNG # use the global rng by default
    internal_nodes = tree.internal_nodes()
    for nd in internal_nodes:
        c = nd.child_nodes()
        rng.shuffle(c)
        nd.set_children(c)

def collapse_conflicting(subtree_root, split, clade_mask):
    """Takes a node that is the root of a subtree.  Collapses every edge in the
    subtree that conflicts with split.  This can include the edge subtending
    subtree_root.
    """
    # we flip splits so that both the split and each edges split  have the
    # lowest bit of the clade mask set to one
    lb = splitmask.lowest_bit_only(clade_mask)

    if lb & split:
        cropped_split = split & clade_mask
    else:
        cropped_split = (~split) & clade_mask

    to_collapse_head_nodes = []
    for nd in subtree_root.postorder_iter(subtree_root):
        if not nd.is_leaf():
            ncm = nd.edge.clade_mask
            if lb & ncm:
                nd_split = ncm & clade_mask
            else:
                nd_split = (~ncm) & clade_mask

            cm_union = nd_split | cropped_split
            if (cm_union != nd_split) and (cm_union != cropped_split):
                to_collapse_head_nodes.append(nd)

    for nd in to_collapse_head_nodes:
        e = nd.edge
        e.collapse()
