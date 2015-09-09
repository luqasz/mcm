# -*- coding: UTF-8 -*-

from mock import MagicMock, patch

from mcm.comparators import UniqueKeyComparator, OrderedComparator


class Test_OrderedComparator:

    def setup(self):
        self.comparator = OrderedComparator()
        self.comparator.SET = MagicMock()
        self.comparator.DEL = MagicMock()
        self.comparator.ADD = MagicMock()
        self.difference = MagicMock()
        self.present = MagicMock()
        self.wanted = MagicMock()

    def test_appends_to_ADD(self):
        """If there is wanted and difference element, append wanted to ADD."""
        self.comparator.decide(wanted=self.wanted, difference=self.difference, present=None )
        self.comparator.ADD.append.assert_called_once_with( self.wanted )

    def test_appends_to_DEL(self):
        """If there is only present element, append it to DEL."""
        self.comparator.decide(wanted=None, difference=None, present=self.present )
        self.comparator.DEL.append.assert_called_once_with( self.present )

    def test_appends_to_SET(self):
        """If there are wanted,difference,present, append difference to SET."""
        self.comparator.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.comparator.SET.append.assert_called_once_with( self.difference )

    def test_calls_setitem_on_difference(self):
        """Assert difference['.id'] was called"""
        present_id = self.present.__getitem__.return_value = MagicMock()
        self.comparator.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.difference.__setitem__.assert_called_once_with('.id', present_id)

    def test_calls_getitem_on_present(self):
        """Assert present['.id'] was called"""
        self.comparator.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.present.__getitem__.assert_called_once_with('.id')


class UniqueKeyComparator_Tests:

    def setup(self):
        self.difference = MagicMock()
        self.present = MagicMock()
        self.wanted = MagicMock()
        self.comparator = UniqueKeyComparator( keys=('name',) )
        self.comparator.ADD = MagicMock()
        self.comparator.SET = MagicMock()
        self.comparator.NO_DELETE = MagicMock()

    def test_appends_to_ADD(self):
        """If there is wanted and difference element, append wanted to ADD."""
        self.comparator.decide(wanted=self.wanted, difference=self.difference, present=None )
        self.comparator.ADD.append.assert_called_once_with( self.wanted)

    def test_appends_to_SET(self):
        """If there are wanted,difference,present, append difference to SET."""
        self.comparator.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.comparator.SET.append.assert_called_once_with( self.difference )

    def test_appends_to_NO_DELETE_if_difference(self):
        """If there are wanted,difference,present elements append present to NO_DELETE."""
        self.comparator.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.comparator.NO_DELETE.append.assert_called_once_with( self.present )

    def test_appends_to_NO_DELETE_if_no_difference(self):
        """If there is wanted,present,append present to NO_DELETE."""
        self.comparator.decide(wanted=self.wanted, difference=None, present=self.present )
        self.comparator.NO_DELETE.append.assert_called_once_with( self.present )

    def test_calls_setitem_on_difference(self):
        """Assert difference['.id'] was called"""
        present_id = self.present.__getitem__.return_value = MagicMock()
        self.comparator.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.difference.__setitem__.assert_called_once_with('.id', present_id)

    def test_calls_getitem_on_present(self):
        """Assert present['.id'] was called"""
        self.comparator.decide(wanted=self.wanted, difference=self.difference, present=self.present )
        self.present.__getitem__.assert_called_once_with('.id')

    @patch('mcm.comparators.CmdPathRow')
    def test_findPair_returns_found_row(self, rowmock):
        self.present.isunique.return_value = True
        found = self.comparator.findPair(searched=self.wanted, present=(self.present,))
        assert found == self.present

    @patch('mcm.comparators.CmdPathRow')
    def test_findPair_returns_empty_CmdPathRow(self, rowmock):
        self.present.isunique.return_value = False
        found = self.comparator.findPair(searched=self.wanted, present=(self.present,))
        assert found == rowmock.return_value

