# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
from unittest import TestCase


from comparators import UniqueKeyComparator, SingleElementComparator, OrderedComparator
from datastructures import CmdPathRow



class OrderedComparator_Tests(TestCase):

    def setUp(self):
        self.TestCls = OrderedComparator()
        self.TestCls.SET = MagicMock()
        self.TestCls.DEL = MagicMock()
        self.TestCls.ADD = MagicMock()
        self.difference = MagicMock()
        self.present = MagicMock()
        self.wanted = MagicMock()

    def test_decide_calls_appen_on_ADD_when_wanted_no_present_and_difference(self):
        self.TestCls.decide(wanted=self.wanted, difference=self.difference, present=None )
        self.TestCls.ADD.append.assert_called_once_with( self.wanted )

    def test_decide_calls_append_on_DEL_when_no_wanted_no_difference_and_present(self):
        self.TestCls.decide(wanted=None, difference=None, present=self.present )
        self.TestCls.DEL.append.assert_called_once_with( self.present )

    def test_decide_calls_append_on_SET_when_wanted_difference_and_present(self):
        self.TestCls.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.TestCls.SET.append.assert_called_once_with( self.difference )

    def test_decide_updates_differences_ID_with_presents_ID(self):
        difference = dict(group='full')
        present = dict(ID=2)
        self.TestCls.decide(wanted=self.wanted, difference=difference, present=present )
        self.assertEqual(difference['ID'], present['ID'])


class OrderedComparator_compare_Tests(TestCase):

    def setUp(self):
        self.wanted_row = CmdPathRow(data=dict(name='admin', group='read'))
        self.present_row = CmdPathRow(data=dict(name='admin', group='full', ID='*2'))
        self.unwanted_row = CmdPathRow(data=dict(name='operator', group='read', ID='*3'))
        self.difference = CmdPathRow(data=dict(group='read', ID='*2'))
        self.TestCls = OrderedComparator()
        self.wanted_data = (self.wanted_row,)
        self.present_data = (self.present_row, self.unwanted_row)

    def test_compare_returns_unwanted_row_in_DEL(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=self.wanted_data, present=self.present_data)
        self.assertEqual(DEL, (self.unwanted_row,))

    def test_compare_returns_all_rows_from_present_in_DEL_when_empty_wanted(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=(), present=self.present_data)
        self.assertEqual(DEL, (self.present_row,self.unwanted_row))

    def test_compare_returns_empty_ADD(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=(), present=self.present_data)
        self.assertEqual(ADD, tuple())

    def test_compare_returns_difference_in_SET(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=self.wanted_data, present=self.present_data)
        self.assertEqual(SET, (self.difference,))




class SingleElementComparator_Tests(TestCase):

    def setUp(self):
        self.present = CmdPathRow(data=dict(group='full'))
        self.wanted = CmdPathRow(data=dict(group='read'))
        self.difference = CmdPathRow(data=dict(group='read'))
        self.TestCls = SingleElementComparator()

    def test_compare_returns_difference_in_SET_when_difference(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=(self.wanted,), present=(self.present,))
        self.assertEqual(SET, (self.difference,))

    def test_compare_returns_empty_SET_when_no_difference(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=(self.present,), present=(self.present,))
        self.assertEqual(SET, tuple())

    def test_compare_returns_empty_ADD(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=(self.wanted,), present=(self.present,))
        self.assertEqual(ADD, tuple())

    def test_compare_returns_empty_DEL(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=(self.wanted,), present=(self.present,))
        self.assertEqual(DEL, tuple())




class UniqueKeyComparator_Tests(TestCase):

    def setUp(self):
        self.present = CmdPathRow(data=dict(group='full', ID='*2', name='admin'))
        self.wanted = CmdPathRow(data=dict(name='admin', group='read'))
        self.difference = CmdPathRow(data=dict(group='read'))
        self.TestCls = UniqueKeyComparator( keys=('name',) )
        self.TestCls.ADD = MagicMock()
        self.TestCls.SET = MagicMock()
        self.TestCls.NO_DELETE = MagicMock()

    def test_decide_calls_append_on_ADD_when_wanted_no_present_and_difference(self):
        self.TestCls.decide(wanted=self.wanted, difference=self.difference, present=None )
        self.TestCls.ADD.append.assert_called_once_with( self.wanted)

    def test_decide_calls_append_on_SET_when_wanted_difference_and_present(self):
        self.TestCls.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.TestCls.SET.append.assert_called_once_with( self.difference )

    def test_decide_calls_append_on_NO_DELETE_when_wanted_difference_and_present(self):
        self.TestCls.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.TestCls.NO_DELETE.append.assert_called_once_with( self.present )

    def test_decide_calls_append_on_NO_DELETE_when_wanted_not_difference_and_present(self):
        self.TestCls.decide(wanted=self.wanted, difference=None, present=self.present )
        self.TestCls.NO_DELETE.append.assert_called_once_with( self.present )

    def test_decide_updates_differences_ID_with_presents_ID(self):
        self.TestCls.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.assertEqual(self.difference['ID'], self.present['ID'])


    def test_findPair_returns_found_row(self):
        found = self.TestCls.findPair(searched=self.wanted, present=(self.present,))
        self.assertEqual(found, self.present)

    def test_findPair_returns_empty_CmdPathRow_when_searched_row_is_not_found(self):
        present = CmdPathRow(data=dict(group='full', ID='*2', name='operator'))
        row = self.TestCls.findPair(searched=self.wanted, present=(present,))
        self.assertEqual(row.data, dict())



class UniqueKeyComparator_compare_Tests(TestCase):

    def setUp(self):
        self.wanted_row = CmdPathRow(data=dict(name='admin', group='read'))
        self.present_row = CmdPathRow(data=dict(name='admin', group='full', ID='*2'))
        self.unwanted_row = CmdPathRow(data=dict(name='operator', group='read', ID='*3'))
        self.difference = CmdPathRow(data=dict(group='read', ID='*2'))
        self.TestCls = UniqueKeyComparator( keys=('name',) )
        self.present = (self.unwanted_row, self.present_row)

    def test_compare_returns_unwanted_row_in_DEL(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=(self.wanted_row,), present=self.present)
        self.assertEqual(DEL, (self.unwanted_row,))

    def test_compare_returns_all_rows_from_present_in_DEL_when_empty_wanted(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=(), present=self.present)
        # objects in DEL may be returned in any order
        self.assertEqual(set(DEL), set((self.unwanted_row,self.present_row)))

    def test_compare_returns_difference_in_SET(self):
        ADD, SET, DEL = self.TestCls.compare(wanted=(self.wanted_row,), present=self.present)
        self.assertEqual(SET, (self.difference,))

    def test_compare_returns_new_row_in_ADD(self):
        new_row = CmdPathRow(data=dict(name='service', group='read'))
        ADD, SET, DEL = self.TestCls.compare(wanted=(new_row,), present=self.present)
        self.assertEqual(ADD, (new_row,))

