from grafeno.transformers.base import Transformer as Base

import spacy

class Transformer (Base):

    def __init__ (self, **kwds):
        super().__init__(**kwds)
        self.__nlp = spacy.load("es_dep_news_trf")
        self._parser = 'spacy'
        self.graph.roots = []

    def parse_text (self, text):
        parse = self.__nlp(text)
        self.graph.spacy_parse = parse
        return parse.sents

    def transform_tree (self, tree):
        self.__root_node = self.__process_node(tree.root)

    def __process_node (self, token):
        temp_id = '_t_{}'.format(token.i)
        self.__current_temp_id = temp_id
        if len(token.morph.get('Person')) == 1: per = token.morph.get("Person")[0]
        else: per = '0'
        if len(token.morph.get('Tense')) == 1: ten = token.morph.get("Tense")[0]
        else: ten = 'None'
        self.nodes[temp_id] = self.transform_node({
            'lemma': token.lemma_,
            'pos': token.pos_.lower(),
            'tag': token.tag_.lower(),
            'spacy_tok': token,
            'person': per,
            'tense': ten
        })
        for c in token.children:
            c_id = self.__process_node(c)
            try:
                self.edges.append(self.transform_dep(c.dep_, temp_id, c_id))
            except KeyError:
                continue
        return temp_id

    def transform_node (self, msnode):
        sem = super().transform_node(msnode)
        sem['id'] = self.__current_temp_id
        return sem

    def post_insertion (self, sentence_nodes):
        super().post_insertion(sentence_nodes)
        try:
            self.graph.roots.append(self._id_map[self.__root_node])
        except KeyError:
            pass

