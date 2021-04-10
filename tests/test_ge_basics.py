from pathlib import Path

import great_expectations as ge
import pandas as pd
import pytest
from great_expectations.core import (
    ExpectationSuiteValidationResult,
    ExpectationSuite,
    ExpectationValidationResult,
)
from great_expectations.dataset import PandasDataset


@pytest.fixture()
def csvpath(tmp_path):
    data = """id,rated,created_at,last_move_at,turns,victory_status,winner,increment_code,white_id,white_rating,black_id,black_rating,moves,opening_eco,opening_name,opening_ply
TTzZc8gW,TRUE,1.50294E+12,1.50294E+12,135,mate,white,10+0,harrygz,2100,dbschultz,1600,c4 e5 Nc3 Nf6 g3 Bc5 Bg2 O-O e3 a6 Nge2 c6 d4 exd4 exd4 Bb4 O-O d5 c5 Bg4 h3 Bh5 g4 Bg6 f4 Be4 Qb3 Bxg2 Kxg2 Ba5 Qxb7 Nbd7 Qxc6 Rc8 Qxa6 Bb4 a3 Nb8 Qd3 Ba5 b4 Bc7 g5 Ng4 Qf3 Nh2 Kxh2 g6 Nxd5 Nc6 Nf6+ Kg7 Qxc6 Bxf4+ Nxf4 Rxc6 d5 Rxf6 Bb2 Qe7 Bxf6+ Qxf6 gxf6+ Kxf6 d6 Ke5 Rfe1+ Kxf4 d7 Kf3 Rad1 Rd8 Re8 Rxd7 Rxd7 f5 Rd4 f4 Rxf4+ Kxf4 Re7 g5 Rxh7 Ke4 Rh5 Kd5 Rxg5+ Kc4 Rg4+ Kb3 Rg3+ Ka4 Rf3 Kb5 Rf6 Ka4 Rb6 Kxa3 Kg2 Kb3 Kf3 Kc4 Ke4 Kc3 c6 Kc4 c7 Kb3 b5 Kb4 Rc6 Kxb5 Rc1 Kb6 c8=N+ Kb7 Ne7 Kb6 Kd5 Kb7 Kd6 Kb6 Rb1+ Ka5 Kc6 Ka4 Kc5 Ka3 Kc4 Ka2 Rb8 Ka3 Ng6 Ka4 Ra8#,A22,English Opening: Carls-Bremen System,5
3ZfA3gFa,TRUE,1.5031E+12,1.5031E+12,23,resign,white,15+15,rookreversal,1217,thegrim123321,1399,c4 e5 Nc3 Nf6 d4 Nc6 d5 Nd4 e3 Nf5 e4 Nd4 Nf3 Nxf3+ Qxf3 Bb4 Bd2 d6 h3 g5 Bxg5 Bxc3+ bxc3,A22,English Opening: King's English Variation |  Two Knights Variation,4
4SrloqB0,TRUE,1.50067E+12,1.50067E+12,46,resign,black,10+5,comped,2001,chesscarl,2105,c4 Nf6 Nc3 e5 g3 d5 cxd5 Nxd5 Bg2 Nb6 Nf3 Nc6 e3 Bd6 d4 O-O O-O Bg4 Qd3 Be6 b3 Be7 Rd1 exd4 Nxd4 Nxd4 Qxd4 Qxd4 exd4 c6 Bb2 Rfd8 Rd3 Rd7 Rad1 Rad8 a4 Bxb3 R1d2 Bb4 Re2 Bc4 Rde3 Bxe2 Nxe2 Nxa4,A22,English Opening: King's English Variation |  Two Knights Variation |  Reversed Dragon,6
dnwPq0Ru,FALSE,1.50077E+12,1.50077E+12,24,resign,black,10+0,mrphaseolusvulgaris,1712,alpv,1959,c4 Nf6 Nc3 e5 e3 Nc6 Be2 b6 d3 Bb7 Nf3 g6 O-O Bg7 Nd2 d5 cxd5 Nxd5 a3 O-O Qc2 Rc8 f4 Nxe3,A22,English Opening: King's English Variation |  Two Knights Variation,4
P459rzus,FALSE,1.50387E+12,1.50388E+12,74,mate,black,15+15,canexd,1104,canid,1500,c4 e5 Nc3 Nf6 d3 Bb4 Bd2 Nc6 a3 Bxc3 bxc3 d5 Qa4 Bd7 Qb3 Na5 Qb4 c6 Qc5 b6 Qe3 dxc4 Qxe5+ Be6 Rb1 cxd3 exd3 O-O Nf3 Nb3 Be3 Re8 c4 Bg4 Qg3 Bxf3 Qxf3 Nd4 Qf4 Nh5 Qg4 Nf6 Qh4 Nf5 Qf4 Nxe3 fxe3 Rb8 Rd1 Qe7 e4 Qxa3 e5 Qe7 d4 c5 Kf2 Nh5 Qf5 g6 Qe4 Rbd8 d5 Qxe5 Qd3 Nf6 Re1 Qxe1+ Kg1 Ng4 Qf3 Qe3+ Qf2 Qxf2#,A22,English Opening: King's English Variation |  Two Knights Variation,4
"""
    csvfile = tmp_path / "data.csv"
    csvfile.write_text(data)
    return csvfile


def test_that_ge_pandas_datasets_are_memory_efficient(csvpath: Path):
    df = pd.read_csv(str(csvpath))
    df_ge = PandasDataset(df)
    bequals = df.values.base == df_ge.values.base
    assert bool(bequals.all())


# this "demo" style test tries out various built in expectations.
# see https://docs.greatexpectations.io/en/latest/reference/glossary_of_expectations.html#dataset
def test_ge_generally(csvpath: Path):
    # a PandasDataset is a pd.Dataframe, unless GE ever switches over to not subclassing
    assert issubclass(PandasDataset, pd.DataFrame)

    df_ge: PandasDataset = ge.read_csv(str(csvpath))

    # check that a column is there
    res: ExpectationSuiteValidationResult = df_ge.expect_column_to_exist("opening_eco")
    assert res.success

    # check that a column value is in the set
    assert df_ge.expect_column_values_to_be_in_set("opening_eco", ["A22"]).success

    # check that things are of expected types
    expected_types = {
        "opening_eco": "object",
        "black_rating": "int64",
        "rated": "bool",
        "created_at": "float64",
    }

    for col, et in expected_types.items():
        assert df_ge.expect_column_values_to_be_of_type(col, et).success

    # there are a bunch of patzers in this dataset ;-) verify that
    # I've spiked harrygz in the test data fixture to have a rating of 2100 in order to simulate a failure
    assert not df_ge.expect_column_values_to_be_between(
        column="white_rating", min_value=500, max_value=2000
    ).success

    # but black is ok! ;-) (chess joke)
    assert not df_ge.expect_column_values_to_be_between(
        column="black_rating", min_value=500, max_value=2000
    ).success

    # great expectations allows you to "save" the suite of expectations you called on a df,
    # and then use that suite generally. let's try it.
    expectation_suite: ExpectationSuite = df_ge.get_expectation_suite()
    assert len(expectation_suite.expectations) == 6
    assert expectation_suite.expectations[0].expectation_type == "expect_column_to_exist"

    # you can just save it do a directory
    suite_save_file = str(csvpath.parent / "suite.json")
    df_ge.save_expectation_suite(filepath=suite_save_file, discard_failed_expectations=False)

    # now lets load it in
    fresh_df: PandasDataset = ge.read_csv(str(csvpath))
    validation_report: ExpectationValidationResult = fresh_df.validate(
        expectation_suite=suite_save_file
    )
    assert not validation_report.success
    assert len(validation_report.results) == 8
    failed_result: ExpectationValidationResult = validation_report.results[7]
    assert not failed_result.success
    assert failed_result.result["partial_unexpected_list"] == [2100, 2001]
