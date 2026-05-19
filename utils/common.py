import os
import pandas as pd

FILE_PATH = "data/clients.xlsx"

COLUMNS = [
    "Client Name", "PAN", "GSTIN", "AY",
    "Document Status", "Audit Status",
    "3CD/3CA Filing Status", "ITR Filing Status",
    "Assigned Staff", "Checklist Completion %"
]


def get_document_status(percentage):
    if percentage == 0:
        return "Pending"
    elif percentage == 100:
        return "Received"
    else:
        return "Partially Received"


def load_clients():
    if os.path.exists(FILE_PATH):
        df = pd.read_excel(FILE_PATH)
    else:
        df = pd.DataFrame(columns=COLUMNS)

    for col in COLUMNS:
        if col not in df.columns:
            if col == "Checklist Completion %":
                df[col] = 0
            elif col == "Document Status":
                df[col] = "Pending"
            elif col == "Audit Status":
                df[col] = "Pending"
            elif col in ["3CD/3CA Filing Status", "ITR Filing Status"]:
                df[col] = "Not Filed"
            else:
                df[col] = ""

    df = df[COLUMNS]
    df["Checklist Completion %"] = df["Checklist Completion %"].fillna(0)
    df["Document Status"] = df["Checklist Completion %"].apply(get_document_status)

    save_clients(df)
    return df


def save_clients(df):
    os.makedirs("data", exist_ok=True)
    df.to_excel(FILE_PATH, index=False)


def get_client_ay(df, selected_client):
    selected_row = df[df["Client Name"] == selected_client].iloc[0]
    return selected_row["AY"]