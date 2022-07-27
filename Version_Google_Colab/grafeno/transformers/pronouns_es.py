from grafeno.transformers.base import Transformer as Base

default_sempos = {
    'noun': 'n',
    'propn': 'n',
    'verb': 'v',
    'adjective': 'j',
    'adj': 'j',
    'adverb': 'r',
    'adv': 'r'
}

class Transformer (Base):

    def __init__ (self, sempos = default_sempos, **kwds):
        super().__init__(**kwds)
        self.__list = sempos.keys()
        self.__dict = sempos

    def transform_node (self, msnode):
        sem = super().transform_node(msnode)
        if msnode.get('pos') == 'pron' and msnode.get('person') == '1':
            sem['concept'] = 'Paciente'
            sem['sempos'] = 'n'
        return sem

    def transform_dep (self, dep, pid, cid):
        edge = super().transform_dep(dep, pid, cid)
        p = self.nodes[pid]
        c = self.nodes[cid]
        if c['concept'] == 'Paciente' and p['sempos'] == 'v':
            edge['functor'] = 'AGENT'
        return edge