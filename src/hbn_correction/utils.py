import numpy as np
import pandas as pd


def long_diagnoses(data: pd.DataFrame) -> pd.DataFrame:
    """Function for converting wide format diagnoses data to long format for data checks."""
    dx_ns = ["Diagnosis_ClinicianConsensus,DX_0" + str(i) for i in range(1, 10)]
    dx_ns.append("Diagnosis_ClinicianConsensus,DX_10")

    vars = [
        "_Confirmed",
        "_Presum",
        "_RC",
        "_RuleOut",
        "_Time",
        "_ByHx",
        "_Spec",
        "_Code",
        "_Past_Doc",
    ]
    all_vars = []
    for var in vars:
        var_list = [str(x) + var for x in dx_ns]
        all_vars.extend(var_list)
    subs = [str(x) + "_Sub" for x in dx_ns]
    cats = [str(x) + "_Cat" for x in dx_ns]

    melted_diagnoses = pd.melt(
        data,
        id_vars=["Identifiers"],
        value_vars=dx_ns,
        var_name="Diagnosis Number",
        value_name="Diagnosis",
    )
    melted_diagnoses["Diagnosis Number"] = melted_diagnoses[
        "Diagnosis Number"
    ].str.extract("(\\d+)")

    melted_subs = pd.melt(
        data,
        id_vars=["Identifiers"],
        value_vars=subs,
        var_name="Diagnosis Number",
        value_name="Subcategory",
    )
    melted_subs["Diagnosis Number"] = melted_subs["Diagnosis Number"].str.extract(
        "(\\d+)"
    )

    melted_cats = pd.melt(
        data,
        id_vars=["Identifiers"],
        value_vars=cats,
        var_name="Diagnosis Number",
        value_name="Category",
    )
    melted_cats["Diagnosis Number"] = melted_cats["Diagnosis Number"].str.extract(
        "(\\d+)"
    )

    melted_vars = pd.melt(
        data,
        id_vars=["Identifiers"],
        value_vars=all_vars,
        var_name="Diagnosis Number",
        value_name="Variable",
    )
    melted_vars["var"] = melted_vars["Diagnosis Number"].str.extract("([^_]+$)")
    melted_vars["Diagnosis Number"] = melted_vars["Diagnosis Number"].str.extract(
        "(\\d+)"
    )

    melted = melted_diagnoses.merge(melted_subs, on=["Identifiers", "Diagnosis Number"])
    melted = melted.merge(melted_cats, on=["Identifiers", "Diagnosis Number"])
    melted = (
        melted_vars.pivot(index=["Identifiers", "Diagnosis Number"], columns="var")
        .stack(0)
        .reset_index()
        .drop(columns="level_2")
        .merge(melted_diagnoses, on=["Identifiers", "Diagnosis Number"])
        .rename(columns={"Doc": "Past_Doc"})
    )

    return melted


def generate_test_data(seed: int) -> pd.DataFrame:
    """Generates test dataset for unit tests."""
    # diagnoses to randomly select from
    rand_diagnoses = [
        "ADHD-Combined Type",
        "Bipolar I Disorder",
        "Conduct Disorder-Unspecified onset",
        "Generalized Anxiety Disorder",
        "Major Depressive Disorder",
        " ",
        "No Diagnosis Given",
        np.nan,
    ]

    data = {}
    # generate test data
    rng = np.random.default_rng(seed=seed)
    for n in [f"{n:02d}" for n in range(1, 11)]:
        for col in [
            "",
            "_Confirmed",
            "_Presum",
            "_RC",
            "_RuleOut",
            "_ByHx",
            "_Time",
            "_Past_Doc",
        ]:
            match col:
                case "":
                    d = rng.choice(rand_diagnoses, 100)
                case _:
                    d = rng.choice([0, 1, np.nan], 100)
            data["Diagnosis_ClinicianConsensus,DX_" + n + col] = d
    return pd.DataFrame(data)
