"""Tests for the data correction functions."""

import itertools
import pytest

from hbn_correction.datacorrection import DataCorrection
from hbn_correction.utils import generate_test_data

data = generate_test_data(seed=11)

test_correction_class = DataCorrection()
test_correction_class.col_base = "Diagnosis_ClinicianConsensus,DX_"


@pytest.mark.unit
def test_input() -> None:
    """Test that invalid input raises an error."""
    with pytest.raises(FileNotFoundError):
        test_correction_class.run("data/wrong_data.csv")


@pytest.mark.unit
def test_correct_nulls():
    """Test that there are no certainty values for null diagnoses."""
    output = test_correction_class._correct_nulls(data)
    for n, col in itertools.product(
        [f"{n:02d}" for n in range(1, 11)],
        ["_Confirmed", "_Presum", "_RC", "_RuleOut", "_ByHx", "_Time", "_Past_Doc"],
    ):
        assert (
            len(
                output[
                    output["Diagnosis_ClinicianConsensus,DX_" + n + col].notnull()
                    & output["Diagnosis_ClinicianConsensus,DX_" + n].isnull()
                ]
            )
            == 0
        )
        assert (
            len(
                output[
                    output["Diagnosis_ClinicianConsensus,DX_" + n + col].notnull()
                    & output["Diagnosis_ClinicianConsensus,DX_" + n]
                    == "No Diagnosis"
                ]
            )
            == 0
        )
        assert (
            len(
                output[
                    output["Diagnosis_ClinicianConsensus,DX_" + n + col].notnull()
                    & output["Diagnosis_ClinicianConsensus,DX_" + n]
                    == "No Diagnosis: Incomplete Eval"
                ]
            )
            == 0
        )


@pytest.mark.unit
def test_correct_byhx():
    """Test that the ByHx column is corrected."""
    output = test_correction_class._correct_byhx(data)
    for n in [f"{n:02d}" for n in range(1, 11)]:
        assert (
            len(
                output[
                    (output["Diagnosis_ClinicianConsensus,DX_" + n + "_ByHx"].isnull())
                    & (
                        (
                            output[
                                "Diagnosis_ClinicianConsensus,DX_" + n + "_Confirmed"
                            ]
                            == 1
                        )
                        | (
                            output["Diagnosis_ClinicianConsensus,DX_" + n + "_Presum"]
                            == 1
                        )
                        | (output["Diagnosis_ClinicianConsensus,DX_" + n + "_RC"] == 1)
                    )
                ]
            )
            == 0
        )


@pytest.mark.unit
def test_correct_confirmed_presum():
    """Test that confirmed and presumptive values are corrected."""
    output = test_correction_class._correct_confirmed_presum(data)
    for n in [f"{n:02d}" for n in range(1, 11)]:
        for v in ["_Confirmed", "_Presum"]:
            assert (
                len(
                    output[
                        (output["Diagnosis_ClinicianConsensus,DX_" + n + v].isnull())
                        & (
                            output["Diagnosis_ClinicianConsensus,DX_" + n]
                            != "No Diagnosis"
                        )
                        & (
                            output["Diagnosis_ClinicianConsensus,DX_" + n]
                            == "No Diagnosis: Incomplete Eval"
                        )
                        & (output["Diagnosis_ClinicianConsensus,DX_" + n].notnull())
                    ]
                )
                == 0
            )


@pytest.mark.unit
def test_correct_past_doc():
    """Test that past documentation values are corrected."""
    output = test_correction_class._correct_past_doc(data)
    for n in [f"{n:02d}" for n in range(1, 11)]:
        assert (
            len(
                output[
                    (
                        output[
                            "Diagnosis_ClinicianConsensus,DX_" + n + "_Past_Doc"
                        ].notnull()
                    )
                    & (output["Diagnosis_ClinicianConsensus,DX_" + n + "_Time"] != 2)
                    & (output["Diagnosis_ClinicianConsensus,DX_" + n + "_ByHx"] != 1)
                ]
            )
            == 0
        )


@pytest.mark.unit
def test_set_past_certainty():
    """Test that past certainty values are set correctly."""
    output = test_correction_class._set_past_certainty(data)
    for n in [f"{n:02d}" for n in range(1, 11)]:
        assert (
            len(
                output[
                    (output["Diagnosis_ClinicianConsensus,DX_" + n + "_Time"] == 2)
                    & (
                        output["Diagnosis_ClinicianConsensus,DX_" + n + "_Past_Doc"]
                        == 1
                    )
                    & (output["Diagnosis_ClinicianConsensus,DX_" + n + "_ByHx"] != 1)
                ]
            )
            == 0
        )
        assert (
            len(
                output[
                    (output["Diagnosis_ClinicianConsensus,DX_" + n + "_Time"] == 2)
                    & (
                        output["Diagnosis_ClinicianConsensus,DX_" + n + "_Past_Doc"]
                        == 3
                    )
                    & (
                        output["Diagnosis_ClinicianConsensus,DX_" + n + "_Confirmed"]
                        != 1
                    )
                ]
            )
            == 0
        )
