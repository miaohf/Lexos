import numpy as np
import pandas as pd
from lexos.helpers.error_messages import SEG_NON_POSITIVE_MESSAGE, \
    NOT_ENOUGH_CLASSES_MESSAGE, EMPTY_DTM_MESSAGE
from lexos.models.topword_model import TopwordModel, TopwordTestOptions
from lexos.receivers.topword_receiver import TopwordAnalysisType


# ---------------------------- Test for z-test ------------------------------
# noinspection PyProtectedMember
class TestZTest:
    def test_normal_case(self):
        assert round(
            TopwordModel._z_test(p1=0.1, p2=0.3, n1=10, n2=1000), 2) == -1.38
        assert round(
            TopwordModel._z_test(p1=0.3, p2=0.1, n1=100, n2=100), 2) == 3.54
        assert TopwordModel._z_test(p1=1, p2=1, n1=100, n2=100) == 0

    def test_special_case(self):
        try:
            _ = TopwordModel._z_test(p1=0.1, p2=0.3, n1=100, n2=0)
            raise AssertionError("Error message did not raise")
        except AssertionError as error:
            assert str(error) == SEG_NON_POSITIVE_MESSAGE

        try:
            _ = TopwordModel._z_test(p1=0.1, p2=0.3, n1=0, n2=100)
            raise AssertionError("Error message did not raise")
        except AssertionError as error:
            assert str(error) == SEG_NON_POSITIVE_MESSAGE
# ---------------------------------------------------------------------------


# ------------------- Test method analyze file to corpus --------------------
# Create test suite for normal case.
test_dtm = pd.DataFrame(data=np.array([(1, 1, 0, 0), (0, 0, 1, 10)]),
                        index=np.array([0, 1]),
                        columns=np.array(["A", "B", "C", "D"]))
test_front_end_option = TopwordAnalysisType.ALL_TO_PARA
test_id_temp_label_map = {0: "F1", 1: "F2"}
test_class_division_map = pd.DataFrame(data=np.array([(True, True)]),
                                       index=["C1"],
                                       columns=[0, 1])
test_option = TopwordTestOptions(doc_term_matrix=test_dtm,
                                 id_temp_label_map=test_id_temp_label_map,
                                 front_end_option=test_front_end_option,
                                 class_division_map=test_class_division_map)
test_topword_model = TopwordModel(test_options=test_option)

# noinspection PyProtectedMember
test_results = test_topword_model._get_result()

# ---------------------------------------------------------------------------
# Create test suite for special case.
test_option_empty = TopwordTestOptions(
    doc_term_matrix=pd.DataFrame(data=[], index=[], columns=[]),
    id_temp_label_map={},
    front_end_option=test_front_end_option,
    class_division_map=pd.DataFrame(data=[], index=[], columns=[]))
test_topword_model_empty = TopwordModel(test_options=test_option_empty)
# ---------------------------------------------------------------------------


class TestParaToGroup:
    def test_normal_case_result(self):
        assert test_results[0]\
               == "Compare Each Document to All the Documents As a Whole."

        assert test_results[1][0]['D'] == -2.1483

        pd.testing.assert_series_equal(
            left=test_results[1][1],
            right=pd.Series([], name='Document "F2" compares to the whole corpus',
                      dtype=None), check_names=False)
    def test_normal_case_header(self):
        assert test_topword_model.get_displayable_result().header \
               == "Compare Each Document to All the Documents As a Whole."

    def test_special_case(self):
        try:
            _ = test_topword_model_empty.get_displayable_result()
            raise AssertionError("Error message did not raise")
        except AssertionError as error:
            assert str(error) == EMPTY_DTM_MESSAGE


# ---------------------------------------------------------------------------


# -------------------- Test method analyze class to all ---------------------
# Create test suit for normal case.
test_dtm = pd.DataFrame(data=np.array([(1, 1, 0, 0, 0, 0, 0, 0),
                                       (0, 0, 1, 1, 0, 0, 0, 0),
                                       (0, 0, 0, 0, 1, 1, 0, 0),
                                       (0, 0, 0, 0, 0, 0, 1, 100)]),
                        index=np.array([0, 1, 2, 3]),
                        columns=np.array(["A", "B", "C", "D",
                                          "E", "F", "G", "H"]))
test_id_temp_label_map = {0: "F1", 1: "F2", 2: "F3", 3: "F4"}
test_front_end_option = TopwordAnalysisType.CLASS_TO_PARA
test_class_division_map = pd.DataFrame(
    data=np.array([(True, True, False, False), (False, False, True, True)]),
    index=np.array(["C1", "C2"]),
    columns=np.array([0, 1, 2, 3]))
test_option = TopwordTestOptions(doc_term_matrix=test_dtm,
                                 id_temp_label_map=test_id_temp_label_map,
                                 front_end_option=test_front_end_option,
                                 class_division_map=test_class_division_map)
test_topword_model_one = TopwordModel(test_options=test_option)

# Create test suit for special case.
test_option_empty = TopwordTestOptions(
    doc_term_matrix=pd.DataFrame(data=[], index=[], columns=[]),
    id_temp_label_map={},
    front_end_option=test_front_end_option,
    class_division_map=pd.DataFrame(data=[], index=[], columns=[]))
test_topword_model_empty_one = TopwordModel(test_options=test_option_empty)


# Testing starts here
class TestClassToAll:
    def test_normal_case_result(self):
        pd.testing.assert_series_equal(
            test_topword_model_one.get_displayable_result().results[0],
            pd.Series([7.2108, 7.2108, -6.3857], index=["A", "B", "H"],
                      name='Document "F1" compares to Class "C2"'))
        pd.testing.assert_series_equal(
            test_topword_model_one.get_displayable_result().results[2],
            pd.Series([], index=[],
                      name='Document "F3" compares to Class "C1"'))

    def test_normal_case_header(self):
        assert test_topword_model_one.get_displayable_result().header == \
               "Compare Each Document to Other Class(es)."

    def test_special_case(self):
        try:
            _ = test_topword_model_empty_one.get_displayable_result()
            raise AssertionError("Error message did not raise")
        except AssertionError as error:
            assert str(error) == EMPTY_DTM_MESSAGE

        try:
            _ = test_topword_model_empty_one.get_displayable_result()
            raise AssertionError("Error message did not raise")
        except AssertionError as error:
            assert str(error) == NOT_ENOUGH_CLASSES_MESSAGE


# ---------------------------------------------------------------------------


# ------------------- Test method analyze class to class --------------------
# Create test suite for normal case.
test_front_end_option = TopwordAnalysisType.CLASS_TO_CLASS
test_option = TopwordTestOptions(doc_term_matrix=test_dtm,
                                 id_temp_label_map=test_id_temp_label_map,
                                 front_end_option=test_front_end_option,
                                 class_division_map=test_class_division_map)
test_topword_model_two = TopwordModel(test_options=test_option)

# Create test suit for special case.
test_option_empty = TopwordTestOptions(
    doc_term_matrix=pd.DataFrame(data=[], index=[], columns=[]),
    id_temp_label_map={},
    front_end_option=test_front_end_option,
    class_division_map=pd.DataFrame(data=[], index=[], columns=[]))
test_topword_model_empty_two = TopwordModel(test_options=test_option_empty)


class TestClassToClass:
    def test_normal_case_result(self):
        pd.testing.assert_series_equal(
            test_topword_model_two.get_displayable_result().results[0],
            pd.Series([-7.70470, 5.09830, 5.09830, 5.09830, 5.09830],
                      index=["H", "A", "B", "C", "D"],
                      name='Class "C1" compares to Class "C2"'))

    def test_normal_case_header(self):
        assert test_topword_model_two.get_displayable_result().header == \
               'Compare a Class to Each Other Class(es).'

    def test_special_case(self):
        try:
            _ = test_topword_model_empty_two.get_displayable_result()
            raise AssertionError("Error message did not raise")
        except AssertionError as error:
            assert str(error) == EMPTY_DTM_MESSAGE

        try:
            _ = test_topword_model_empty_two.get_displayable_result()
            raise AssertionError("Error message did not raise")
        except AssertionError as error:
            assert str(error) == NOT_ENOUGH_CLASSES_MESSAGE
# ---------------------------------------------------------------------------
