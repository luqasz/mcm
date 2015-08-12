
class SentenceEquality:

    def assertApiSentenceEqual(self, snt1, snt2, msg=None):
        '''
        Order in witch api words appear in sentence does not matter.
        Tuples must be casted to sets in order to prevent random test fails.
        '''
        return self.assertSetEqual(set(snt1), set(snt2), msg=msg)
