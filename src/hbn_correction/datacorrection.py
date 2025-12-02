"""Fix ClinicianConsensusDiagnosis Data."""

from pathlib import Path
import numpy as np
import pandas as pd


class DataCorrection:
    dx_ns = [f"{n:02d}" for n in range(1, 11)]

    def _correct_nulls(
        cls,
        df: pd.DataFrame,
        #    n: int,
    ) -> pd.DataFrame:
        for n in cls.dx_ns:
            # fix certainty values for null or not given diagnoses
            d_col = cls.col_base + n
            for c in [
                "Confirmed",
                "Presum",
                "RC",
                "RuleOut",
                "ByHx",
                "Time",
                "Past_Doc",
            ]:
                cert_col = cls.col_base + n + "_" + c
                null_condition = (
                    (df[d_col] == "No Diagnosis Given")
                    | (df[d_col] == "No Diagnosis Given: Incomplete Eval")
                    | (pd.isna(df[d_col]))
                )
                df[cert_col] = np.where(null_condition, np.nan, df[cert_col])
        return df

    def _correct_byhx(
        cls,
        df: pd.DataFrame,
        #   i: int,
        #   n: str,
    ) -> pd.DataFrame:
        # if any of confirmed, presum, or RC are 1, if ByHx is NULL, ByHx should be 0
        for n in cls.dx_ns:
            any_cert = (
                (df[cls.col_base + n + "_Confirmed"] == 1)
                | (df[cls.col_base + n + "_Presum"] == 1)
                | (df[cls.col_base + n + "_RC"] == 1)
                | (df[cls.col_base + n + "_RuleOut"] == 1)
            )

            df[cls.col_base + n + "_ByHx"] = np.where(
                (any_cert) & pd.isna(df[cls.col_base + n + "_ByHx"]),
                0,
                df[cls.col_base + n + "_ByHx"],
            )
        return df

    def _correct_confirmed_presum(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        for n in cls.dx_ns:
            not_null = (
                (~pd.isna(df[cls.col_base + n]))
                & (df[cls.col_base + n] != "No Diagnosis Given")
                & (df[cls.col_base + n] != "No Diagnosis Given: Incomplete Eval")
            )
            missing_confirm_presum = (pd.isna(df[cls.col_base + n + "_Confirmed"])) & (
                pd.isna(df[cls.col_base + n + "_Presum"])
            )
            other_cert = (
                (df[cls.col_base + n + "_RC"] == 1)
                | (df[cls.col_base + n + "_RuleOut"] == 1)
                | (df[cls.col_base + n + "_ByHx"] == 1)
            )

            df[cls.col_base + n + "_Confirmed"] = np.where(
                not_null & missing_confirm_presum,
                np.where(
                    other_cert,
                    0,
                    1,
                ),
                df[cls.col_base + n + "_Confirmed"],
            )
            df[cls.col_base + n + "_Presum"] = np.where(
                not_null & missing_confirm_presum,
                0,
                df[cls.col_base + n + "_Presum"],
            )
        return df

    def _correct_past_doc(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        for n in cls.dx_ns:
            current_diagnosis = (df[cls.col_base + n + "_ByHx"] != 1) & (
                df[cls.col_base + n + "_Time"] != 2
            )
            # Past Doc should only be noted if ByHx is 1 or Time is 2
            df[cls.col_base + n + "_Past_Doc"] = np.where(
                current_diagnosis,
                np.nan,
                df[cls.col_base + n + "_Past_Doc"],
            )
        return df

    def _set_past_certainty(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        for n in cls.dx_ns:
            past_diagnosis = df[cls.col_base + n + "_Time"] == 2
            missing_certainty = (
                (df[cls.col_base + n + "_Confirmed"] != 1)
                & (df[cls.col_base + n + "_Presum"] != 1)
                & (df[cls.col_base + n + "_RC"] != 1)
                & (df[cls.col_base + n + "_RuleOut"] != 1)
                & (df[cls.col_base + n + "_ByHx"] != 1)
            )
            reported_ksads = df[cls.col_base + n + "_Past_Doc"] == 3
            with_doc = df[cls.col_base + n + "_Past_Doc"] == 1

            df[cls.col_base + n + "_Confirmed"] = np.where(
                past_diagnosis & missing_certainty & reported_ksads,
                1,
                df[cls.col_base + n + "_Confirmed"],
            )

            df[cls.col_base + n + "_ByHx"] = np.where(
                past_diagnosis & missing_certainty & with_doc,
                1,
                df[cls.col_base + n + "_ByHx"],
            )
        return df

    def run(cls, hbn_data_path: str) -> pd.DataFrame:
        """Fixes errors and missing values in the diagnostic data and saves as csv.

        This function fixes known inconsistencies or errors in the HBN Clinician Consensus
        Diagnosis Data. As the data entry template for this dataset has changed over time,
        participants may be missing values for columns that were not present at the time
        of data entry. The changes to the certainty columns include:
            - When a diagnosis is Null or "No Diagnosis Given", the certainty columns
            are all set to null
            - When one of confirmed, presumptive, or requires confirmation are 1, if by
            history is missing, it should be set to 0.
            - When confirmed and presumptive are missing, if requires confirmation, rule
            out, and by history are all 0, confirmed should be 1 and presumptive 0. These
            are confirmed diagnoses from an old template version with no explicit
            "confirmed" option.
            - When confirmed and presumptive are missing, if one of requires confirmation,
            rule out, or by history are 1, confirmed and presumptive should both be 0.
            - If a diagnoses is by history, the time variable should be blank.
            - Past Documentation should only be noted for diagnoses by history or past
            diagnoses. Otherwise, this variable should be blank.
            - The "New", "PRem", and "Rem" columns are from an outdated template version and
            should be removed. This information is available elsewhere.

        Args:
            hbn_data_path (str): The path to the HBN data file.

        Returns:
            None
        """
        # load data
        path = Path(hbn_data_path)
        if not path.exists():
            raise FileNotFoundError(f"File {path} not found.")
        df = pd.read_csv(
            hbn_data_path,
            # set col with mixed dtype
            dtype={"Diagnosis_ClinicianConsensus,DX_10_Spec": str},
        )

        if "Diagnosis_ClinicianConsensus,DX_01" in df.columns.to_list():
            cls.col_base = "Diagnosis_ClinicianConsensus,DX_"
        elif "DX_01" in df.columns.to_list():
            cls.col_base = "DX_"
        else:
            raise ValueError("Invalid column names.")

        df["Identifiers"] = df["Identifiers"].str.split(",").str[0]

        dx_ns = [f"{n:02d}" for n in range(1, 11)]

        text_cols = df.select_dtypes(include=["object"]).columns

        # strip whitespace and replace empty strings with None for text columns
        df[text_cols] = (
            df[text_cols]
            .apply(lambda x: x.str.strip())
            .replace(to_replace={"nan", "", " "}, value=None)
        )
        df[text_cols] = df[text_cols].replace(np.nan, None)

        # corrections
        # remove any certainty values for null or not given diagnoses
        df = cls._correct_nulls(df)
        # fill missing by history
        df = cls._correct_byhx(df)
        # fill missing confirmed and presumptive data
        df = cls._correct_confirmed_presum(df)
        # remove incorrect past doc data
        df = cls._correct_past_doc(df)
        # set missing past diagnosis certainty based on past_doc values
        df = cls._set_past_certainty(df)
        # remove unnecessary columns
        for n in dx_ns:
            df = df.drop(columns=[cls.col_base + n + "_New"])
            # Remove remission columns (Remission and Partial Remission)
            df = df.drop(columns=[cls.col_base + n + "_Rem"])
            df = df.drop(columns=[cls.col_base + n + "_PRem"])

        print("Data corrections completed.")
        save_path = hbn_data_path.replace(".csv", "_corrected.csv")
        df.to_csv(save_path, index=False)
        print(f"Corrected data was saved to {save_path}")
        return df
