# -*- coding: UTF-8 -*-

import pytest

from mcm.comparators import UniqueKeyComparator, SingleElementComparator, OrderedComparator
from mcm.datastructures import CmdPathRow


@pytest.fixture
def compare_data(request):
    single = {
        'wanted':CmdPathRow({"primary-ntp":"1.1.1.1"}),
        'present':CmdPathRow({"primary-ntp":"213.222.193.35"}),
        'difference':CmdPathRow({"primary-ntp":"1.1.1.1"}),
    }
    default = {
        'wanted':CmdPathRow({'name':'admin', 'group':'read'}),
        'present':CmdPathRow({'name':'admin', 'group':'full', '.id':'*2'}),
        'extra':CmdPathRow({'name':'operator', 'group':'read', '.id':'*3'}),
        'difference':CmdPathRow({'group':'read', '.id':'*2'}),
    }
    if 'single' in request.cls.__name__.lower():
        return single
    else:
        return default



class Test_SingleComparator:

    def setup(self):
        self.comparator = SingleElementComparator()

    def test_difference_in_SET(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(compare_data['wanted'],), present=(compare_data['present'],))
        assert SET == (compare_data['difference'],)

    def test_empty_SET_when_same_data(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(compare_data['wanted'],), present=(compare_data['wanted'],))
        assert SET == tuple()

    def test_empty_SET_when_empty_wanted(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=tuple(), present=(compare_data['present'],))
        assert SET == tuple()

    def test_empty_ADD(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(compare_data['wanted'],), present=(compare_data['present'],))
        assert ADD == tuple()

    def test_empty_DEL(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(compare_data['wanted'],), present=(compare_data['present'],))
        assert DEL == tuple()



class Test_OrderedComparator:

    def setup(self):
        self.comparator = OrderedComparator()

    def test_extra_in_DEL(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(compare_data['wanted'],), present=(compare_data['present'],compare_data['extra']))
        assert DEL == (compare_data['extra'],)

    def test_present_in_DEL_when_empty_wanted(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(), present=(compare_data['present'], compare_data['extra']))
        assert DEL == (compare_data['present'], compare_data['extra'])

    def test_empty_ADD_when_empty_wanted(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(), present=(compare_data['present'],))
        assert ADD == tuple()

    def test_difference_in_SET(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(compare_data['wanted'],), present=(compare_data['present'],))
        assert SET == (compare_data['difference'],)



class Test_UniqueKeyComparator:

    def setup(self):
        self.comparator = UniqueKeyComparator( keys=('name',) )

    def test_extra_in_DEL(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(compare_data['wanted'],), present=(compare_data['present'], compare_data['extra']))
        assert DEL == (compare_data['extra'],)

    def test_present_in_DEL_when_empty_wanted(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(), present=(compare_data['present'], compare_data['extra']))
        # compare sets instead of tuples. order in witch objects exist in DEL does not matter
        assert set(DEL) == set((compare_data['present'], compare_data['extra']))

    def test_compare_returns_difference_in_SET(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(compare_data['wanted'],), present=(compare_data['present'],compare_data['extra']))
        assert SET == (compare_data['difference'],)

    def test_wanted_in_ADD(self, compare_data):
        ADD, SET, DEL = self.comparator.compare(wanted=(compare_data['wanted'],), present=())
        assert ADD == (compare_data['wanted'],)
