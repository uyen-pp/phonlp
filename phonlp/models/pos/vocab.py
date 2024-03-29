from collections import Counter, OrderedDict

from phonlp.models.common.vocab import EMPTY, EMPTY_ID, VOCAB_PREFIX, BaseMultiVocab, BaseVocab, CompositeVocab


class CharVocab(BaseVocab):
    def build_vocab(self):
        if type(self.data[0][0]) is list:  # general data from DataLoader
            counter = Counter([c for sent in self.data for w in sent for c in w[self.idx]])
            for k in list(counter.keys()):
                if counter[k] < self.cutoff:
                    del counter[k]
        else:  # special data from Char LM
            counter = Counter([c for sent in self.data for c in sent])
        self._id2unit = VOCAB_PREFIX + list(
            sorted(list(counter.keys()), key=lambda k: (counter[k], k), reverse=True)
        )  # list [VOCAB_PREFIX, a,b,c] by frequent of character
        self._unit2id = {w: i for i, w in enumerate(self._id2unit)}  # dictionary c: id


class WordVocab(BaseVocab):
    def __init__(self, data=None, lang="", idx=0, cutoff=0, lower=False, ignore=[]):
        self.ignore = ignore
        super().__init__(data, lang=lang, idx=idx, cutoff=cutoff, lower=lower)
        self.state_attrs += ["ignore"]

    def id2unit(self, id):
        if len(self.ignore) > 0 and id == EMPTY_ID:
            return "_"
        else:
            return super().id2unit(id)

    def unit2id(self, unit):
        if len(self.ignore) > 0 and unit in self.ignore:
            return self._unit2id[EMPTY]
        else:
            return super().unit2id(unit)

    def build_vocab(self):
        if self.idx==2:
            rels = [
                'mod',
                'amr-unknown',
                'in',
                'arg0',
                'quantity',
                'arg1',
                'polarity',
                'arg3',
                'root',
                'out',
                'domain-of',
                'location',
                'time',
                'example',
                'conj',
                'purpose',
                'manner',
                'arg4',
                'arg2',
                'direction',
                'compared-to',
                'accompanier',
                'topic',
                'extent',
                'mode',
                'vocative',
                'condition',
                'date',
                'cause-of',
                'instrument',
                'degree',
                'concession',
                'organization',
                'arg5',
                'country',
                'medium',
                'name',
                'order',
                'poss-of',
                'range',
                'source',
                'target',
                'unit',
                'day',
                'month',
                'value',
                'year'
            ]
            self._id2unit = VOCAB_PREFIX + rels
            self._unit2id = {w: i for i, w in enumerate(self._id2unit)}
        else:
            if self.lower:
                counter = Counter([w[self.idx].lower() for sent in self.data for w in sent])
            else:
                counter = Counter([w[self.idx] for sent in self.data for w in sent])
            for k in list(counter.keys()):
                if counter[k] < self.cutoff or k in self.ignore:
                    del counter[k]

            
class XPOSVocab(CompositeVocab):
    def __init__(self, data=None, lang="", idx=0, sep="", keyed=False):
        super().__init__(data, lang, idx=idx, sep=sep, keyed=keyed)


class FeatureVocab(CompositeVocab):
    def __init__(self, data=None, lang="", idx=0, sep="", keyed=False):
        super().__init__(data, lang, idx=idx, sep=sep, keyed=keyed)


class MultiVocab(BaseMultiVocab):
    def state_dict(self):
        """ Also save a vocab name to class name mapping in state dict. """
        state = OrderedDict()
        key2class = OrderedDict()
        for k, v in self._vocabs.items():
            state[k] = v.state_dict()
            key2class[k] = type(v).__name__
        state["_key2class"] = key2class
        return state

    @classmethod
    def load_state_dict(cls, state_dict):
        class_dict = {
            "CharVocab": CharVocab,
            "WordVocab": WordVocab,
            "XPOSVocab": XPOSVocab,
            "FeatureVocab": FeatureVocab,
        }
        new = cls()
        assert "_key2class" in state_dict, "Cannot find class name mapping in state dict!"
        key2class = state_dict.pop("_key2class")
        for k, v in state_dict.items():
            classname = key2class[k]
            new[k] = class_dict[classname].load_state_dict(v)
        return new
