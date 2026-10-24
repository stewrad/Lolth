import io
import pandas as pd
from pathlib import Path


def load_data(path):
    path = Path(path)

    extension = path.suffix.lower()

    if extension == ".txt":
        return mread(path)

    elif extension == ".pkl":
        return pd.read_pickle(path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

def load_multiple(paths):

    paths = [Path(p) for p in paths]

    if not paths:
        raise ValueError("No files selected")

    txt_files = [
        p for p in paths
        if p.suffix.lower() == ".txt"
    ]

    pkl_files = [
        p for p in paths
        if p.suffix.lower() == ".pkl"
    ]

    if len(txt_files) + len(pkl_files) != len(paths):
        raise ValueError("Selection contains unsupported file types")

    datasets = []

    if txt_files:
        datasets.append(mread(txt_files))

    for path in pkl_files:
        datasets.append(pd.read_pickle(path))

    return pd.concat(datasets, ignore_index=True)

def mread(paths):
    if isinstance(paths, (str, Path)):
        paths = [paths]

    files = [Path(p) for p in paths]

    # path = Path(path)

    def nest_data(group):
        a_data = group["A1"].to_numpy()
        i_data = group["I"].to_numpy()
        q_data = group["Q"].to_numpy()
        pdb_data = group["PdB"].to_numpy()

        return a_data, i_data, q_data, pdb_data

    col_names = [
        "P1", "E1", "A1",
        "P2", "E2", "A2",
        "I", "Q", "PdB"
    ]

    all_blocks = []
    for fPath in files:

        current_block = []
        inside_block = False
        freq = None

        if not fPath.is_file():
            raise FileNotFoundError(fPath)

        with fPath.open("r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.strip()

                if "frequency" in clean_line.lower():
                    numeric_str = clean_line.lower().replace(
                        "frequency", ""
                    )
                    freq = float(numeric_str.split()[0])
                    continue

                if clean_line.lower() == "start data":
                    inside_block = True
                    continue

                elif clean_line.lower() == "end data":
                    inside_block = False

                    if current_block:
                        df_block = pd.read_csv(
                            io.StringIO("\n".join(current_block)),
                            sep=r"\s+",
                            header=None,
                            names=col_names
                        )

                        df_block["File"] = fPath.name
                        df_block["Freq"] = freq

                        df_block["P"] = (
                            df_block["P1"].astype(str).str.replace("'", "", regex=False)
                            + df_block["P2"].astype(str).str.replace("'", "", regex=False)
                        )

                        all_blocks.append(df_block)
                        current_block = []

                    continue

                if inside_block:
                    current_block.append(clean_line)

            if current_block:
                raise ValueError(
                    f"Unterminated data block in {fPath.name}"
                )

    if not all_blocks:
        raise ValueError("No measurement data found in file")

    flat_df = pd.concat(all_blocks, ignore_index=True)

    group_columns = [
        "File", "Freq", "P", "E1", "E2"
    ]

    rdata = (
        flat_df.groupby(group_columns, sort=False)
        .apply(nest_data, include_groups=False)
        .reset_index(name="Data")
    )

    return rdata