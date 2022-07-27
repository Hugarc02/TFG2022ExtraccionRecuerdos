from grafeno.transformers.wordnet import Transformer as WNGet

class Transformer (WNGet):
    '''Finds the wordnet-defined `class' of a concept.

    Parameters
    ----------
    concept_class_hypernyms : bool
        If True, a new node is added with the class concept, related to the
        original node by an ``HYP'' edge.
    '''

    def transform_node (self, msnode):
        sem = super().transform_node(msnode)
        sempos = sem.get('sempos')
        if sempos == 'v':
            if msnode.get('person') == '1' or (msnode.get('person') == '3' and msnode.get('tense') == 'Imp'):
                chyp = { 'concept': 'Paciente', 'sempos': 'n'}
                self.sprout(sem['id'], 'AGENT', chyp)
        return sem
