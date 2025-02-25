"""Tests for the data correction functions."""

import itertools
import pytest

from hbn_correction.datacorrection import DataCorrection
from hbn_correction.utils import generate_test_data

data = generate_test_data(seed=11)


def test_input() -> None:
    """Test that invalid input raises an error."""
    with pytest.raises(FileNotFoundError):
        DataCorrection().run("data/wrong_data.csv")


def test_null_replacements():
    """Test that there are no certainty values for null diagnoses."""
    output = DataCorrection()._correct_nulls(data)
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


def test_byhx_correction():
    """Test that the ByHx column is corrected."""
    output = DataCorrection()._correct_byhx(data)
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


def test_confirmedpresum_conrrection():
    """Test that confirmed and presumptive values are corrected."""
    output = DataCorrection()._correct_confirmed_presum(data)
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


def test_pastdoc_correction():
    """Test that past documentation values are corrected."""
    output = DataCorrection()._correct_past_doc(data)
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
