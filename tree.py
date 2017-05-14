class Node(object):
    def __init__(self, start, end):
        self.start = start
        self.end   = end
        self.next  = {}
        self.link  = -1

    def edge_length(self, pos):
        return min(self.end, pos + 1) - self.start

class Tree(object):

    def _print_leaves(self, x):
        s = ''

        if len(self.nodes[x].next) == 0:
            return '\tnode%d [label="",shape=point]\n' % x
        else:
            for c in self.nodes[x].next:
                s += self._print_leaves(self.nodes[x].next[c])

        return s

    def _print_internal_nodes(self, x):
        s = ''

        if x != self.root and len(self.nodes[x].next) == 0:
            s += '\tnode%d [label=\"\",style=filled,fillcolor=lightgrey,shape=circle,width=.07,height=.07]\n' % x

        for c in self.nodes[x].next:
            s += self._print_internal_nodes(self.nodes[x].next[c])

        return s

    def _edge_string(self, x):
        start = self.nodes[x].start
        end = min(self.nodes[x].end, self.position + 1)
        return self.text[start : end] + '(%d-%d)' % (start, end)

    def _print_edges(self, x):
        s = ''

        for c in self.nodes[x].next:
            s += '\tnode%d -> node%d [label="%s",weight=3]\n' % (x, self.nodes[x].next[c], self._edge_string(self.nodes[x].next[c]))
            s += self._print_edges(self.nodes[x].next[c])

        return s

    def _print_suffix_links(self, x):
        s = ''

        if self.nodes[x].link > 0:
            s += '\tnode%d -> node%d [label="",weight=1,style=dotted]\n' % (x, self.nodes[x].link)

        for c in self.nodes[x].next:
            s += self._print_suffix_links(self.nodes[x].next[c])

        return s

    def __repr__(self):
        s  = 'digraph {\n'
        s += '\trankdir = LR;\n'
        s += '\tedge [arrowsize=0.4,fontsize=10]\n'
        s += '\tnode1 [label="",style=filled,fillcolor=lightgrey,shape=circle,width=.1,height=.1];\n'
        s += '//------leaves------\n'
        s += self._print_leaves(self.root)
        s += '//------internal nodes------\n'
        s += self._print_internal_nodes(self.root)
        s += '//------edges --------\n'
        s += self._print_edges(self.root)
        s += '//----- suffix links ----\n'
        s += self._print_suffix_links(self.root)
        s += '}\n'

        return s

    def __init__(self):
        self.text             = ''
        self.root             = 0
        self.nodes            = [Node(-1, -1)]
        self.active_node      = 0
        self.active_edge      = 0
        self.active_length    = 0
        self.remainder        = 0
        self.max              = 1e11
        self.current_node     = 0
        self.need_suffix_link = -1
        self.position         = -1

    # append new node and return its index (aka current count of nodes)
    def add_node(self, start, end):
        self.nodes.append(Node(start, end))
        self.current_node += 1

        return self.current_node

    def walk_down(self, next):
        next_node      = self.nodes[next]
        nn_edge_length = next_node.edge_length(self.position)

        # is the length of what we try to "insert" but can not because it already
        # exists longer than the current edge? Than we're past it and can
        # "move" after what we have already "inserted"
        if self.active_length >= nn_edge_length:
            self.active_edge   += nn_edge_length
            self.active_length -= nn_edge_length
            self.active_node    = next

            return True

        return False

    def add_suffix_link(self, node_index):

        if self.need_suffix_link > 0:
            self.nodes[self.need_suffix_link].link = node_index

        self.need_suffix_link = node_index

    def add_char(self, c):
        self.position         += 1
        self.text             += c
        self.remainder        += 1
        self.need_suffix_link  = -1

        while (self.remainder > 0):
            if self.active_length == 0:
                self.active_edge = self.position

            # "virtual" current character
            _c = self.text[self.active_edge]

            # does the node we're working on not have the character yet?
            if _c not in self.nodes[self.active_node].next:
                leaf = self.add_node(self.position, self.max)

                # pointer behind _c points to new node
                self.nodes[self.active_node].next[_c] = leaf
                self.add_suffix_link(self.active_node)

            else:
                # get node behind already existing character
                next_index = self.nodes[self.active_node].next[_c]
                next_node  = self.nodes[next_index]

                # try to walk to the end of the already found suffix since the
                # next character is not part of what we have already matched.
                # Check the condition in method
                if (self.walk_down(next_index)):
                    continue

                # if the next character is already registered in the current
                # suffix, we increase the active_length
                if self.text[next_node.start + self.active_length] == c:
                    self.active_length += 1
                    self.add_suffix_link(self.active_node)

                    break

                # ???
                split_index = self.add_node(next_node.start, next_node.start + self.active_length)
                self.nodes[self.active_node].next[_c] = split_index

                leaf = self.add_node(self.position, self.max)
                self.nodes[split_index].next[c] = leaf

                next_node.start += self.active_length
                self.nodes[split_index].next[self.text[next_node.start]] = next_index

                self.add_suffix_link(split_index)

            self.remainder -= 1

            if self.active_node == self.root and self.active_length > 0:
                self.active_length -= 1
                self.active_edge    = self.position - self.remainder + 1
            else:
                if self.nodes[self.active_node].link > 0:
                    self.active_node = self.nodes[self.active_node].link
                else:
                    self.active_node = self.root

string = 'abcabxabcd'
T = Tree()
for i in range(len(string)):
    T.add_char(string[i])

print T
